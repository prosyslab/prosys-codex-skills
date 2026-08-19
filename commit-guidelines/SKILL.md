---
name: commit-guidelines
description: Prepare, validate, and create focused Git commits with safe staging and strict message formatting. Use when Codex is asked to commit changes, amend a commit message, review commit readiness, or fix a repository commit message.
---

# Commit Guidelines

Use this skill whenever the user asks to commit, amend a commit message, or
check whether current changes are ready to commit.

## Workflow

1. Inspect the complete worktree state before staging:

   ```sh
   git status --short
   git diff
   git diff --stat
   ```

2. Identify the files belonging to the requested change. Preserve unrelated
   tracked and untracked files. Stage explicit paths only; never use broad
   commands such as `git add .` or `git add -A` when unrelated files exist.

3. Validate the change before committing:

   - Run the narrowest relevant test while iterating.
   - Run `make test` before every commit.
   - For touched OCaml or Dune files, run `dune build @fmt`.
   - Run `git diff --check`.
   - Review `git diff --cached` after staging and confirm that it is one
     coherent behavioral change.

   Do not weaken tests, suppress alarms, disable analysis, or hide failures
   merely to make validation pass. If a test result changes, diagnose why and
   update expectations only when the change is intentional and justified.

4. Create the commit only after validation succeeds. Each commit must pass
   `make test` independently and should contain one important behavioral
   change. Keep incidental cleanup separate unless it is required by the fix.

5. Verify the result:

   ```sh
   git show -s --format='%H%n%B' HEAD
   git status --short
   ```

   Report the commit hash, validation results, and any intentionally preserved
   untracked files.

## Commit message format

Use exactly this structure:

```text
[Topic] concise summary

Detailed explanation of the cause and the important implementation choice.
Wrap every body line at 72 characters.

Co-authored-by: Codex
```

Follow these rules:

- Use one concise subject line beginning with a concrete topic such as
  `[Program]`, `[Sparrow]`, `[Sparrow][Worklist]`, `[Sparrow][Rust]`, or
  `[Test]`.
- Leave exactly one blank line between the subject and the body.
- Explain the root cause and the important functional change, not the work
  process.
- Wrap every body line, including the attribution line, at 72 characters.
- Leave one blank line before `Co-authored-by: Codex`.
- When the user asks for the core change only, omit refactoring details from
  the message even if refactoring is included in the implementation.
- Include `Co-authored-by: Codex` in the detailed message for Codex-authored
  commits.

Before amending a message, use `git show` and `git status` to confirm that the
request is message-only. Use `git commit --amend` without changing the staged
content, then verify the new message and status.

## Safe staging and recovery

Resolve the exact change with read-only inspection before staging. Do not stage
generated output, temporary analysis directories, logs, or unrelated user
files. Do not delete, reset, or check out user changes to repair a commit.

If the repository is a submodule and Git metadata is outside the writable
workspace, request the required permission for the Git operation and keep the
file paths being staged explicit.
