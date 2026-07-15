#!/usr/bin/env python3
"""Safely resolve and write files in an explicit Obsidian vault."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from typing import NoReturn

DEFAULT_VAULT = "notes"


def fail(message: str, exit_code: int = 1) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


class ObsidianVault:
    def __init__(self, vault: str) -> None:
        self.vault = vault
        self.executable = shutil.which("obsidian")
        if self.executable is None:
            macos_executable = Path("/Applications/Obsidian.app/Contents/MacOS/obsidian")
            if macos_executable.is_file():
                self.executable = str(macos_executable)
            else:
                fail("Obsidian CLI was not found on PATH")

        root_output = self._run("vault", "info=path")
        if not root_output:
            fail(f"Obsidian did not return a path for vault {vault!r}")
        self.root = Path(root_output).expanduser().resolve()
        if not self.root.is_dir():
            fail(f"Resolved vault path is not a directory: {self.root}")

    def _run(self, *arguments: str) -> str:
        command = [self.executable, f"vault={self.vault}", *arguments]
        # Keep the caller's stdin available for Markdown piped to this helper.
        # Some Obsidian CLI launchers read inherited stdin even when the command
        # itself does not need input, which would otherwise consume heredocs
        # before read_stdin() can process them.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            stdin=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or f"exit status {result.returncode}"
            fail(f"Obsidian CLI command failed: {detail}")
        return result.stdout.strip()

    def daily_relative_path(self) -> str:
        output = self._run("daily:path")
        if not output:
            fail(f"Obsidian did not return a daily-note path for vault {self.vault!r}")
        return self.validate_relative_path(output)

    def validate_relative_path(self, value: str) -> str:
        normalized = value.replace("\\", "/")
        relative = PurePosixPath(normalized)
        if relative.is_absolute() or ".." in relative.parts:
            fail(f"Vault path must be relative and cannot contain '..': {value!r}")
        if not relative.parts or str(relative) in {"", "."}:
            fail("Vault path cannot be empty")
        return str(relative)

    def absolute_path(self, relative_path: str) -> Path:
        validated = self.validate_relative_path(relative_path)
        candidate = (self.root / validated).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            fail(f"Path resolves outside the Obsidian vault: {relative_path!r}")
        return candidate

    def open(self, relative_path: str) -> None:
        self._run("open", f"path={self.validate_relative_path(relative_path)}")


def read_stdin() -> str:
    if sys.stdin.isatty():
        fail("Markdown content must be provided on stdin")
    content = sys.stdin.read()
    if not content.strip():
        fail("Refusing to write empty Markdown content")
    return content


def append_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_separator = False
    if path.exists() and path.stat().st_size > 0:
        with path.open("rb") as existing:
            existing.seek(-1, os.SEEK_END)
            needs_separator = existing.read(1) != b"\n"

    with path.open("a", encoding="utf-8") as note:
        if needs_separator:
            note.write("\n")
        note.write(content)
        if not content.endswith("\n"):
            note.write("\n")


def print_result(vault: ObsidianVault, relative_path: str) -> None:
    print(
        json.dumps(
            {
                "vault": vault.vault,
                "relative_path": relative_path,
                "absolute_path": str(vault.absolute_path(relative_path)),
            },
            indent=2,
        )
    )


def command_info(vault: ObsidianVault, _args: argparse.Namespace) -> None:
    daily_relative = vault.daily_relative_path()
    print(
        json.dumps(
            {
                "vault": vault.vault,
                "vault_root": str(vault.root),
                "daily_relative_path": daily_relative,
                "daily_absolute_path": str(vault.absolute_path(daily_relative)),
            },
            indent=2,
        )
    )


def command_daily_path(vault: ObsidianVault, _args: argparse.Namespace) -> None:
    print_result(vault, vault.daily_relative_path())


def command_path(vault: ObsidianVault, args: argparse.Namespace) -> None:
    print_result(vault, vault.validate_relative_path(args.path))


def command_daily_append(vault: ObsidianVault, args: argparse.Namespace) -> None:
    relative_path = vault.daily_relative_path()
    append_markdown(vault.absolute_path(relative_path), read_stdin())
    if args.open:
        vault.open(relative_path)
    print_result(vault, relative_path)


def command_create(vault: ObsidianVault, args: argparse.Namespace) -> None:
    relative_path = vault.validate_relative_path(args.path)
    absolute_path = vault.absolute_path(relative_path)
    content = read_stdin()
    absolute_path.parent.mkdir(parents=True, exist_ok=True)

    mode = "w" if args.overwrite else "x"
    try:
        with absolute_path.open(mode, encoding="utf-8") as note:
            note.write(content)
            if not content.endswith("\n"):
                note.write("\n")
    except FileExistsError:
        fail(f"Note already exists; use append or explicitly pass --overwrite: {relative_path}")

    if args.open:
        vault.open(relative_path)
    print_result(vault, relative_path)


def command_append(vault: ObsidianVault, args: argparse.Namespace) -> None:
    relative_path = vault.validate_relative_path(args.path)
    absolute_path = vault.absolute_path(relative_path)
    if not absolute_path.is_file():
        fail(f"Note does not exist; use create first: {relative_path}")
    append_markdown(absolute_path, read_stdin())
    if args.open:
        vault.open(relative_path)
    print_result(vault, relative_path)


def command_read(vault: ObsidianVault, args: argparse.Namespace) -> None:
    relative_path = vault.validate_relative_path(args.path)
    absolute_path = vault.absolute_path(relative_path)
    if not absolute_path.is_file():
        fail(f"Note does not exist: {relative_path}")
    sys.stdout.write(absolute_path.read_text(encoding="utf-8"))


def command_list(vault: ObsidianVault, args: argparse.Namespace) -> None:
    folder = vault.absolute_path(args.folder)
    if not folder.is_dir():
        fail(f"Folder does not exist: {args.folder}")
    for path in sorted(folder.rglob("*.md")):
        print(path.relative_to(vault.root).as_posix())


def command_search(vault: ObsidianVault, args: argparse.Namespace) -> None:
    if args.limit < 1:
        fail("Search limit must be greater than 0")

    needle = args.query if args.case_sensitive else args.query.casefold()
    matches = []
    truncated = False

    for discovered_path in sorted(vault.root.rglob("*.md")):
        relative_path = discovered_path.relative_to(vault.root).as_posix()
        relative_parts = PurePosixPath(relative_path).parts
        if any(part.startswith(".") for part in relative_parts):
            continue

        is_daily_note = relative_parts[0] == "Daily"
        if args.scope == "daily" and not is_daily_note:
            continue
        if args.scope == "other" and is_daily_note:
            continue

        # Re-resolve every result through the vault boundary check before reading.
        path = vault.absolute_path(relative_path)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as error:
            fail(f"Could not read note {relative_path!r}: {error}")

        for line_number, line in enumerate(lines, start=1):
            haystack = line if args.case_sensitive else line.casefold()
            if needle not in haystack:
                continue
            if len(matches) == args.limit:
                truncated = True
                break
            matches.append(
                {
                    "path": relative_path,
                    "line": line_number,
                    "text": line.strip(),
                }
            )

        if truncated:
            break

    if args.json:
        print(
            json.dumps(
                {
                    "query": args.query,
                    "scope": args.scope,
                    "case_sensitive": args.case_sensitive,
                    "limit": args.limit,
                    "truncated": truncated,
                    "matches": matches,
                },
                indent=2,
            )
        )
        return

    for match in matches:
        print(f"{match['path']}:{match['line']}: {match['text']}")

    match_label = "match" if len(matches) == 1 else "matches"
    suffix = f" (limited to the first {args.limit})" if truncated else ""
    print(f"\n{len(matches)} {match_label}{suffix}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT", DEFAULT_VAULT),
        help=f"Explicit Obsidian vault name (default: $OBSIDIAN_VAULT or {DEFAULT_VAULT!r})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Show the resolved vault and daily-note paths")
    info_parser.set_defaults(handler=command_info)

    daily_path_parser = subparsers.add_parser("daily-path", help="Show today's daily-note paths")
    daily_path_parser.set_defaults(handler=command_daily_path)

    path_parser = subparsers.add_parser("path", help="Resolve a vault-relative path")
    path_parser.add_argument("--path", required=True)
    path_parser.set_defaults(handler=command_path)

    daily_append_parser = subparsers.add_parser("daily-append", help="Append stdin to today's daily note")
    daily_append_parser.add_argument("--open", action="store_true", help="Open the note in Obsidian")
    daily_append_parser.set_defaults(handler=command_daily_append)

    create_parser = subparsers.add_parser("create", help="Create a note from stdin")
    create_parser.add_argument("--path", required=True)
    create_parser.add_argument("--overwrite", action="store_true")
    create_parser.add_argument("--open", action="store_true", help="Open the note in Obsidian")
    create_parser.set_defaults(handler=command_create)

    append_parser = subparsers.add_parser("append", help="Append stdin to an existing note")
    append_parser.add_argument("--path", required=True)
    append_parser.add_argument("--open", action="store_true", help="Open the note in Obsidian")
    append_parser.set_defaults(handler=command_append)

    read_parser = subparsers.add_parser("read", help="Read an existing note")
    read_parser.add_argument("--path", required=True)
    read_parser.set_defaults(handler=command_read)

    list_parser = subparsers.add_parser("list", help="List Markdown notes beneath a vault folder")
    list_parser.add_argument("--folder", required=True)
    list_parser.set_defaults(handler=command_list)

    search_parser = subparsers.add_parser("search", help="Search Markdown note content")
    search_parser.add_argument("query", help="Literal text to find")
    search_parser.add_argument(
        "--scope",
        choices=("daily", "other", "all"),
        default="all",
        help="Search Daily/, everything outside Daily/, or both (default: all)",
    )
    search_parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Match case exactly (default: case-insensitive)",
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of matches to return (default: 50)",
    )
    search_parser.add_argument("--json", action="store_true", help="Return structured JSON")
    search_parser.set_defaults(handler=command_search)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    vault = ObsidianVault(args.vault)
    args.handler(vault, args)


if __name__ == "__main__":
    main()
