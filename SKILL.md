---
name: code-restore-point
description: |
  Create Git stash restore points (snapshots) before code modifications, record modification notes,
  and restore to the pre-modification state at any time. Trigger before any code modification.
  Typical scenarios:
  - User says "help me change xxx", "modify xxx", "refactor xxx", "adjust xxx"
  - User wants to edit, modify, or rewrite files, code, or projects
  - User is concerned about breaking things and says "backup first" or "in case I need to revert"
tags:
  - openclaw
  - openclaw-skill
  - code-backup
  - git-stash
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

Uses Git stash to create lightweight snapshots. Execute `create` before modifying any code to
record current state + modification intent; execute `restore` to fully revert the workspace
to the pre-modification state.

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
Restore point [#1] created.
[Perform modification...]
Modification complete. To revert, say "restore to restore point #1".
```

## Notes

- The current workspace must be a Git repository (non-repo directories will error)
- After restoring, that record is removed from the index (prevents double-apply)
- Stash includes all modifications (tracked + untracked files)
- Multiple modifications can create multiple restore points, ordered by time
- Cleanup command removes orphaned records no longer present in the stash list
