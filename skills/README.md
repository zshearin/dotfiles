# Agent skills

Reusable personal [Agent Skills](https://agentskills.io/) live here so they can be versioned in the dotfiles repository and installed on any machine.

Each child directory containing a `SKILL.md` is one skill:

```text
skills/
├── install.sh
└── obsidian-notes/
    ├── SKILL.md
    └── scripts/
        └── obsidian_notes.py
```

## Installation

### Requirements

The included `obsidian-notes` skill requires:

- Python 3
- Obsidian with its CLI available as `obsidian`
- An Obsidian vault with Daily Notes configured

Confirm the CLI is available:

```bash
obsidian version
obsidian vaults verbose
```

### Install for Pi and other Agent Skills-compatible tools

Run the installer:

```bash
~/dotfiles/skills/install.sh
```

By default, it creates one symlink per skill under the standard global directory:

```text
~/.agents/skills/obsidian-notes
  -> ~/dotfiles/skills/obsidian-notes
```

Pi discovers `~/.agents/skills/` automatically. Restart the agent session after installing a new skill so discovery runs again.

The installer is idempotent: running it again is safe. It refuses to replace an existing file, directory, or unrelated symlink.

### Install for a harness-specific directory

If an agent harness does not discover `~/.agents/skills/`, pass its skills directory explicitly:

```bash
~/dotfiles/skills/install.sh ~/.claude/skills
```

For example:

```bash
# Standard Agent Skills location; use this for Pi
~/dotfiles/skills/install.sh

# Claude-specific location, only if needed
~/dotfiles/skills/install.sh ~/.claude/skills

# Codex-specific location, only if needed
~/dotfiles/skills/install.sh ~/.codex/skills
```

Do not install the same skill into multiple directories loaded by one harness. Duplicate skill names can cause discovery warnings.

### Verify installation

```bash
ls -l ~/.agents/skills/obsidian-notes
```

For the Obsidian skill, verify its configured paths without writing anything:

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py info
```

Expected shape:

```json
{
  "vault": "notes",
  "vault_root": "/Users/you/path/to/vault",
  "daily_relative_path": "Daily/2026-07-14.md",
  "daily_absolute_path": "/Users/you/path/to/vault/Daily/2026-07-14.md"
}
```

## Updating skills

Because installation uses symlinks, edits or Git updates under `~/dotfiles/skills/` become available immediately. Start a new agent session when a skill's metadata or trigger description changes so the harness can rediscover it.

On a new machine:

```bash
git clone <dotfiles-repository-url> ~/dotfiles
~/dotfiles/skills/install.sh
```

## Using `obsidian-notes`

The `obsidian-notes` skill writes personal notes and maintains persistent implementation plans without guessing the vault's filesystem location.

It supports two main workflows:

1. Quick captures appended to today's daily note.
2. Implementation plans stored under `0-Now/<Project>/` and updated while the agent executes them.

### Configure the vault

The default vault name is `notes`. To use a different vault, set `OBSIDIAN_VAULT`:

```bash
export OBSIDIAN_VAULT="Personal"
```

Add that export to the machine's shell configuration if it should apply to every session.

The skill always targets an explicit vault and resolves its paths through the Obsidian CLI:

```bash
obsidian vault="${OBSIDIAN_VAULT:-notes}" vault info=path
obsidian vault="${OBSIDIAN_VAULT:-notes}" daily:path
```

It never assumes that the currently active Obsidian vault is the intended one and never hardcodes a machine-specific vault root.

### Invoke the skill naturally

After restarting the agent session, prompts that explicitly mention Obsidian should activate the skill:

```text
Write this to my Obsidian daily note: remember to review the proposal tomorrow.
```

```text
Capture these investigation findings in Obsidian.
```

```text
Add a note under my existing Boeh Company Location Guard project.
```

```text
Create an Obsidian implementation plan for this refactor, then execute it.
```

### Invoke the skill explicitly in Pi

Use the skill command when you want to guarantee it is loaded:

```text
/skill:obsidian-notes
```

Arguments can follow the command:

```text
/skill:obsidian-notes capture this in today's daily note: follow up on the API design
```

```text
/skill:obsidian-notes plan the catalog permissions refactor in Obsidian, then execute it
```

### Note routing

The skill uses these defaults:

| Content | Destination |
|---|---|
| Quick thought, reminder, short work log | Today's Daily Note |
| Active implementation plan | `0-Now/<Project>/Implementation Plan - <Topic>.md` |
| Notes for an existing active project | Existing `0-Now/<Project>/` folder |
| Unclassified material | `4-ToSort or Inbox/<Title>.md` |
| Durable technical reference | Appropriate folder under `2-Other/` |
| Team-owned canonical documentation | Source repository, not personal Obsidian |
| Completed implementation plan | Remains with the project unless explicitly archived |

When placement is genuinely ambiguous, the agent asks one focused question rather than guessing.

### Implementation-plan workflow

When asked to plan and execute, the agent:

1. Investigates the relevant repository instructions and code.
2. Creates `0-Now/<Project>/Implementation Plan - <Topic>.md`.
3. Records the goal, constraints, investigation, concrete checklist, and validation commands.
4. Reads the saved plan before modifying code.
5. Completes one checkbox at a time.
6. Updates the execution log with discoveries and validation evidence.
7. Revises the plan before deviating from it.
8. Marks the plan complete and records the outcome after final validation.
9. Reports both the vault-relative and absolute note paths.

Personal working strategy belongs in Obsidian. Documentation that teammates or repository tooling depend on belongs in the source repository.

## Using the helper directly

Most of the time, prompt the agent rather than invoking the helper yourself. These commands are useful for testing or scripting.

### Show vault and daily-note paths

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py info
```

### Append to today's daily note

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py daily-append <<'MARKDOWN'
- Remember to review the proposal tomorrow.
MARKDOWN
```

### Create a note

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py create \
  --path "0-Now/Example Project/Notes - API Design.md" <<'MARKDOWN'
# API Design

Initial notes.
MARKDOWN
```

Creation refuses to overwrite an existing note. Use `append` when adding to one:

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py append \
  --path "0-Now/Example Project/Notes - API Design.md" <<'MARKDOWN'

## Follow-up

Additional findings.
MARKDOWN
```

### Read a note

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py read \
  --path "0-Now/Example Project/Notes - API Design.md"
```

### Open a note after writing

Pass `--open` to `create`, `append`, or `daily-append`:

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py daily-append --open <<'MARKDOWN'
- Open this daily note after appending.
MARKDOWN
```

### Select a different vault for one command

```bash
python3 ~/dotfiles/skills/obsidian-notes/scripts/obsidian_notes.py \
  --vault "Personal" info
```

## Safety behavior

The Obsidian helper:

- Resolves the vault root and daily note through the Obsidian CLI.
- Requires vault-relative paths.
- Rejects absolute paths and `..` traversal.
- Safely handles multiline Markdown.
- Refuses accidental overwrites.
- Reports the relative and absolute paths after writing.

The skill also instructs agents not to store credentials, access tokens, secrets, or sensitive customer data in Obsidian.

## Troubleshooting

### The skill is not available

1. Run `~/dotfiles/skills/install.sh`.
2. Confirm `~/.agents/skills/obsidian-notes` exists.
3. Start a new agent session.
4. In Pi, invoke `/skill:obsidian-notes` explicitly.

### The Obsidian CLI is not found

Confirm Obsidian is installed and try:

```bash
command -v obsidian
/Applications/Obsidian.app/Contents/MacOS/obsidian version
```

The helper checks both `PATH` and the standard macOS application location.

### The wrong vault is selected

Inspect known vaults:

```bash
obsidian vaults verbose
```

Then set the intended name:

```bash
export OBSIDIAN_VAULT="Personal"
```

Or pass `--vault` for one helper invocation.

### Daily Notes are not configured

Check whether Obsidian can resolve today's note:

```bash
obsidian vault=notes daily:path
```

If it returns no path, configure and enable Daily Notes in that vault before using `daily-append`.
