#!/usr/bin/env bash
set -euo pipefail

skills_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target_root="${1:-$HOME/.agents/skills}"

mkdir -p "$target_root"

installed=0
for skill_file in "$skills_dir"/*/SKILL.md; do
  [[ -e "$skill_file" ]] || continue

  source_dir="$(dirname "$skill_file")"
  skill_name="$(basename "$source_dir")"
  target="$target_root/$skill_name"

  if [[ -L "$target" ]]; then
    existing_source="$(readlink "$target")"
    if [[ "$existing_source" == "$source_dir" ]]; then
      echo "Already installed: $target -> $source_dir"
      installed=$((installed + 1))
      continue
    fi
    echo "Refusing to replace existing symlink: $target -> $existing_source" >&2
    exit 1
  fi

  if [[ -e "$target" ]]; then
    echo "Refusing to replace existing path: $target" >&2
    exit 1
  fi

  ln -s "$source_dir" "$target"
  echo "Installed: $target -> $source_dir"
  installed=$((installed + 1))
done

if [[ "$installed" -eq 0 ]]; then
  echo "No skills found beneath $skills_dir" >&2
  exit 1
fi
