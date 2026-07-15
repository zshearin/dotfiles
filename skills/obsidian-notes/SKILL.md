---
name: obsidian-notes
description: Write, append, organize, and retrieve notes in the user's Obsidian vault. Use when the user explicitly mentions Obsidian, a daily note, writing something down, capturing a thought, or creating a persistent Markdown implementation plan in personal notes before executing it. Always target an explicit vault, route quick captures to the daily note, and keep active implementation plans under 0-Now/<Project>/.
compatibility: Requires Python 3 and the Obsidian CLI. Defaults to the `notes` vault; override with OBSIDIAN_VAULT.
---

# Obsidian Notes

Write personal notes and persistent implementation plans without guessing where the Obsidian vault lives.

## Non-negotiable rules

1. Always target an explicit vault. Use `$OBSIDIAN_VAULT` when set; otherwise use `notes`.
2. Never infer the vault root from the current working directory or hardcode an absolute vault path.
3. Resolve the vault root and daily-note path through the Obsidian CLI.
4. Use `scripts/obsidian_notes.py` for file access. It validates that paths remain inside the resolved vault and safely handles multiline Markdown.
5. Never overwrite an existing note unless the user explicitly requests replacement.
6. Do not put credentials, access tokens, secrets, or sensitive customer data in Obsidian.
7. Report the vault-relative and absolute path after every write.
8. If the user explicitly asks for Obsidian, use this skill rather than routing the note to another personal knowledge system.
9. Add a small set of relevant Obsidian hashtags to every new daily capture, regular note, and implementation plan.
10. Search note content with the helper's `search` command rather than grepping or scanning the vault directly.

## Establish context first

Resolve `scripts/obsidian_notes.py` relative to this `SKILL.md` before running it. Do not assume the agent's current working directory is the skill directory. Either invoke the resolved absolute script path or explicitly change to the skill directory first. The examples below assume the latter:

```bash
cd <directory-containing-this-SKILL.md>
python3 scripts/obsidian_notes.py info
```

This returns the selected vault, resolved vault root, and today's daily-note paths. If it fails, stop and explain whether the Obsidian CLI, vault, or daily-note configuration could not be found.

To select another vault for one operation:

```bash
python3 scripts/obsidian_notes.py --vault "Personal" info
```

Do not silently fall back to the active Obsidian vault.

## Search notes

Use the helper to search Markdown content across daily notes, other vault notes, or both. Searches are literal and case-insensitive by default, and results include the vault-relative path, line number, and matching line. Hidden vault directories such as `.obsidian` and `.trash` are excluded.

Search only daily notes under `Daily/`:

```bash
python3 scripts/obsidian_notes.py search "worktree" --scope daily
```

Search notes outside `Daily/`:

```bash
python3 scripts/obsidian_notes.py search "implementation plan" --scope other
```

Search the entire vault (daily and other notes); `all` is the default scope:

```bash
python3 scripts/obsidian_notes.py search "#herdr" --scope all
```

Useful options:

```bash
# Exact case
python3 scripts/obsidian_notes.py search "GraphQL" --case-sensitive

# Return more than the default 50 matches
python3 scripts/obsidian_notes.py search "#git" --limit 100

# Structured output for follow-up processing
python3 scripts/obsidian_notes.py search "rollout" --scope all --json
```

Use the `read` command to inspect a matched note when more context is needed. Do not expose sensitive matched content in summaries or external messages.

## Route the note

| User intent | Destination |
|---|---|
| Quick thought, reminder, work log, or short capture | Today's daily note |
| Active implementation strategy | `0-Now/<Project>/Implementation Plan - <Topic>.md` |
| Notes for an existing active project | Existing `0-Now/<Project>/` folder |
| Material with no clear home | `4-ToSort or Inbox/<Descriptive title>.md` |
| Durable technical reference | The appropriate topic folder under `2-Other/` |
| Team-owned canonical documentation | The source repository, not Obsidian |
| Completed implementation plan | Keep it with the project unless the user asks to archive it under `3-Archived/` |

Prefer an existing `0-Now/<Project>/` folder when one clearly matches. List paths without reading private note contents:

```bash
python3 scripts/obsidian_notes.py list --folder "0-Now"
```

Ask one focused question if project placement is genuinely ambiguous. Otherwise write immediately and report the result.

## Add relevant hashtags

Tag every new daily section, regular note, and implementation plan with a concise `Tags:` line immediately below its heading. Choose tags from the actual subject and context; do not add every familiar tag indiscriminately.

```markdown
## World worktree workflow

Tags: #worktree #git #world #local
```

Tagging rules:

- Use 2–5 lowercase hashtags, with hyphens for multiword tags.
- Prefer durable subject/tool/context tags such as `#worktree`, `#git`, `#world`, `#local`, or `#herdr`.
- Add `#local` for local-development setup or machine-local workflows; do not use it for unrelated notes.
- Add `#herdr` only when the note is actually about HerdR.
- Do not automatically add `#obsidian` unless Obsidian itself is the subject.
- For a one-line daily bullet, put the hashtags at the end of that bullet instead of creating a separate `Tags:` line.
- When appending to an existing section or note, reuse its existing tags. Add a new tag only when the appended material introduces a durable new subject, and avoid duplicate tag lines.
- Do not encode credentials, customer identifiers, incident secrets, or other sensitive information in tags.

## Quick capture workflow

Append concise, useful Markdown to today's daily note:

```bash
python3 scripts/obsidian_notes.py daily-append <<'MARKDOWN'
- Captured thought or result. #relevant-topic #context
MARKDOWN
```

Use a short heading and a tag line when appending more than a single bullet:

```markdown
## Topic

Tags: #relevant-topic #context

Summary, context, and any next action.
```

Do not run `obsidian daily` merely to locate the file. `daily:path` is the source of truth and the helper resolves it without relying on the active file.

## Create or update a regular note

Create a new note without overwriting an existing file:

```bash
python3 scripts/obsidian_notes.py create \
  --path "0-Now/Project/Notes - Topic.md" <<'MARKDOWN'
# Topic

Tags: #relevant-topic #context

Content.
MARKDOWN
```

Append to an existing note:

```bash
python3 scripts/obsidian_notes.py append \
  --path "0-Now/Project/Notes - Topic.md" <<'MARKDOWN'

## New finding

Content.
MARKDOWN
```

Read it back when accuracy matters:

```bash
python3 scripts/obsidian_notes.py read \
  --path "0-Now/Project/Notes - Topic.md"
```

Add `--open` to `create`, `append`, or `daily-append` only when the user wants the note opened in Obsidian.

## Persistent implementation-plan workflow

Use this workflow when the user asks to strategize an implementation in Markdown and then execute it.

### 1. Investigate before planning

Read relevant repository instructions and code first. Record facts rather than guesses. Do not modify production code yet.

### 2. Create the plan

Store it at:

```text
0-Now/<Project>/Implementation Plan - <Topic>.md
```

Use this template:

```markdown
---
type: implementation-plan
status: active
created: YYYY-MM-DD
source_repository: owner/repository
source_path: repository-relative or World path
source_branch: branch-name
---

# <Goal>

Tags: #implementation-plan #relevant-project #relevant-domain

## Goal

Describe the observable outcome and what success means.

## Context and constraints

- Relevant architecture and conventions
- User requirements
- Safety, compatibility, and rollout constraints

## Investigation

- Files and systems inspected
- Existing patterns to follow
- Important findings and unresolved assumptions

## Plan

- [ ] Concrete step naming the affected file, class, or function
- [ ] Next concrete implementation step
- [ ] Add or update appropriate coverage
- [ ] Run focused validation
- [ ] Run final checks

## Validation

- Focused test or check commands
- Final validation commands
- Any manual verification required

## Execution log

Record discoveries, deviations, and command results while implementing.

## Outcome

Fill this in after execution.
```

Replace the placeholder hashtags with tags specific to the project and domain. Omit unavailable metadata rather than inventing it. Use repository-relative paths where possible; never store a machine-specific source path unless it is necessary.

### 3. Execute from the plan

1. Read the saved plan before modifying code.
2. Work one unchecked item at a time.
3. After each completed item, update its checkbox and append concise evidence to `Execution log`.
4. If a discovery invalidates the plan, update the plan before diverging. Explain what changed and why.
5. Follow all repository-specific development and testing instructions; this skill does not override them.
6. Do not claim a checkbox is complete until the corresponding work and validation have actually happened.

### 4. Close the plan

After final validation:

- Change `status: active` to `status: complete`.
- Check completed items.
- Fill in `Outcome` with the implemented behavior, validation evidence, and any follow-up work.
- Report both the code result and the plan's vault-relative and absolute paths.

If execution is paused or blocked, leave the status as `active` or change it to `blocked`, preserve unchecked items, and record the blocker.

## Editing safety

- Prefer `append` for additive notes.
- To change an existing plan, read it, make a targeted edit with the coding agent's normal file-editing tool using the absolute path returned by `path`, then read it back. Do not reconstruct and overwrite the entire note casually.
- Use the helper's `create --overwrite` only when the user explicitly requests complete replacement.
- Before moving an existing note, use the Obsidian CLI `move` command so Obsidian can maintain links.
