---
name: code-restore-point
description: |
  Create Git HEAD commit snapshots before code modifications, record modification notes,
  and restore to the pre-modification state at any time. Trigger before any code modification.
  Typical scenarios:
  - User says "help me change xxx", "modify xxx", "refactor xxx", "adjust xxx"
  - User wants to edit, modify, or rewrite files, code, or projects
  - User is concerned about breaking things and says "backup first" or "in case I need to revert"
tags:
  - openclaw
  - openclaw-skill
  - code-backup
  - restore-point
  - snapshot
  - code-protection
  - git-tools
  - developer-tools
  - automation
  - refactoring
  - rollback
---

# Code Restore Point (code-restore-point)

## How It Works

Before any code modification, record the current HEAD commit SHA. After modification is complete,
the user can restore the entire workspace to that exact snapshot state using `git reset --hard`.

- Uncommitted changes are automatically committed before creating the snapshot
- Supports workspaces with or without initial commits (auto-initializes if needed)
- After restore, that snapshot is removed from the index (prevents double-apply)
- Restore point entries that reference deleted commits are auto-cleaned via `cleanup`

## Usage

### 1. Before Modification - Create Restore Point

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py create <modification-note>
```

Example:
```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py create "Fix login page layout misalignment"
```

Equivalent AI instruction:
> "Create a restore point, I'm about to modify config.json"
> "I need to change this code, please back it up first"

### 2. List Restore Points

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py list
```

### 3. Restore - When You Need to Revert

```bash
# Restore to specific index
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py restore 0

# Restore to the last restore point (most common)
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py restore-last
```

### 4. Cleanup Orphaned Records

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py cleanup
```

## AI Agent Workflow

When the user wants to modify code, the AI should:

1. Immediately create a restore point (before any file operations)
2. Tell the user the restore point ID
3. Perform the code modification
4. Report completion status and provide the revert command

AI instruction example:
```
I am about to modify [file/code]. Creating a restore point first...
[Create restore point]
Restore point [#1] created (HEAD: abc1234).
[Perform modification...]
Modification complete. To revert, say "restore to restore point #1".
```

## Technical Details

- Works in any Git repository (auto-initializes if no commits exist)
- Snapshot = current HEAD commit SHA (git reset --hard on restore)
- Uncommitted changes are auto-committed before snapshot (no data loss)
- Index stored at `.restore-points.json` in workspace root
- Windows GBK console compatible (UTF-8 output)
