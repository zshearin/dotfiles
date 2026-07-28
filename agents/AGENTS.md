# Personal agent preferences

## General

- Keep responses concise. Only report to me in ASD-STE100 Simplified Technical English
- Investigate existing code before making changes.
- Do not commit or push unless explicitly requested.
- Run relevant tests after modifying code.
- Explain potentially destructive commands before running them and ask me if it's okay first.

## Coding preferences

- Prefer simple, maintainable solutions.
- Follow the existing style of the repository.
- Avoid suppressing type or lint errors.

## Markdown file routing

- When I ask to create, write, or save a Markdown file without specifying a repository path, default to my Obsidian `notes` vault.
- Load and follow the `obsidian-notes` skill for these requests.
- Do not create the file in the current repository unless I explicitly say it belongs in the repository, provide a repository-relative path, or request canonical repository documentation such as a README.
- Store active plans under `0-Now/<Project>/`.
- If the destination is genuinely ambiguous, ask whether I want Obsidian or the repository before writing.
