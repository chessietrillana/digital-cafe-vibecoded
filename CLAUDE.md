# Project: Digital Cafe (Vibecoded)

This project recreates "Digital Cafe," a web app for a coffee shop where
users browse products, add them to a cart, and check out. This is a course
assignment about vibecoding: I have already built this same app by
hand in a previous exercise, and I am now rebuilding it using an agentic
coding workflow instead, to compare the two experiences.

## Hard Rules (do not break these)

- You (the AI) will write all code. I will not write code
  directly — only give instructions, review your output, and approve
  merges.
- Do NOT clone, fetch, browse, search for, or otherwise reference any
  external repository, walkthrough, tutorial, or reference solution for
  this project — even if one is mentioned in conversation or referenced. 
  Build this app solely from the feature descriptions, tech
  stack, and instructions I give directly in this project. This
  rule is non-negotiable.
- Work only through the terminal / this coding harness. Do not suggest or
  rely on GUI-based tools, hosted app builders, or services outside this
  terminal session.

## Required Workflow

For every feature or change, follow this exact five-step process, in
order. Do not skip a step or combine steps unless I explicitly
says to skip ahead (e.g. for a trivial one-line fix or typo).

1. **study** — Analyze my request and write a Markdown file in
   `doc/study/` that discusses it: feasibility, tradeoffs, relevant parts
   of the existing codebase, open questions, and design options. The more
   specific my request, the more specific this doc should be. Do
   not write any code at this step. Name the file descriptively, e.g.
   `doc/study/0001-user-auth.md`.

2. **plan** — Based on the study, write a checklist Markdown file in
   `doc/plan/` detailing the concrete, ordered steps needed to achieve the
   outcome. Name it to match the study, e.g. `doc/plan/0001-user-auth.md`.

3. **execute plan** — Take the plan doc and actually execute it, on a
   separate Git branch off `main` (e.g. `feat/user-auth`), checking off
   steps as you go and committing in logical chunks rather than one giant
   commit.

4. **rendezvous** — Merge the feature branch back into `main` and make
   sure the codebase is in a workable state: verify the app actually
   runs, resolve any conflicts, do not leave `main` broken.

5. **sync docs** — Ensure the living documentation in `doc/wiki/` is
   up-to-date with the current state of the codebase (models, routes,
   features, setup instructions). Treat `doc/wiki/` as a manual, not a
   changelog.

## Commit Conventions

All changes must be scoped to Conventional Commits:
- `feat:` — a new feature
- `fix:` — a bug fix
- `chore:` — maintenance, config, tooling
- `build:` — build system or dependency changes
- `docs:` — documentation-only changes (including doc/study, doc/plan, doc/wiki)
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `test:` — adding or fixing tests

Keep each commit scoped to a single logical change.

## Folder Reference

- `doc/study/` — feasibility/tradeoff analysis docs, one per feature
- `doc/plan/` — checklist implementation docs, one per feature
- `doc/wiki/` — living manual of the current codebase, kept in sync after every rendezvous

## Tech Stack

Django + SQLite. Do not substitute a different framework or database
without discussing it in a study doc first.

## Notes for the Agent

- Ask for clarification in the study doc's "Open Questions" section
  rather than guessing silently on ambiguous requirements.
- Confirm files are actually written to disk (e.g. via `ls`) after
  writing them, rather than just reporting success.