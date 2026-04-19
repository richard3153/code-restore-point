# Code Restore Point (代码还原点)

[English](#english) | [中文](#中文)

---

## English

### Overview

`code-restore-point` is an OpenClaw skill that creates Git HEAD commit snapshots of your workspace before any code modification. It records the current HEAD commit SHA, allowing you to instantly revert to that exact state using `git reset --hard` at any time.

### Use Cases

- **Batch refactoring**: Snapshot before restructuring a large module, restore if anything breaks
- **Risky experiments**: Test a new library or pattern without fear — one command to go back
- **Collaborative code review**: Create a restore point before applying suggested changes
- **Learning and exploring**: Safely modify unfamiliar codebases
- **CI/CD breaking fixes**: Before touching shared configs, snapshot first

### Key Features

- **One-command snapshot**: Records current HEAD commit SHA; auto-commits any uncommitted changes first
- **Named restore points**: Attach a note to each snapshot so you know what it's for
- **Instant rollback**: `git reset --hard` to the recorded commit — full workspace restored
- **Auto-initialize**: Works in non-Git directories (auto-initializes if needed)
- **Clean index**: Automatically removes consumed restore points to prevent double-apply
- **Orphan cleanup**: Safely prunes stale records referencing deleted commits

### Installation

#### Option 1: Via GitHub Release (Recommended)

1. Download the latest `.skill` package from the [Releases](https://github.com/richard3153/code-restore-point/releases) page
2. Place it in your OpenClaw skills directory:
   ```
   C:\Users\<YourUser>\.qclaw\skills\code-restore-point\
   ```
3. Or use the OpenClaw skill install command if available

#### Option 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/richard3153/code-restore-point.git ~/.qclaw/skills/code-restore-point

# The skill is ready to use
```

### Usage

#### Before Modifying Code — Create Restore Point

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py create <note>
```

Example:
```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py create "Refactor user authentication module"
```

#### List All Restore Points

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py list
```

#### Restore to a Specific Point

```bash
# By index (shown in list output)
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py restore 0
```

#### Restore to the Most Recent Point

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py restore-last
```

#### Cleanup Orphaned Records

```bash
python ~/.qclaw/skills/code-restore-point/scripts/create_restore_point.py cleanup
```

### AI Agent Workflow

When the user asks to modify code, the AI agent should:

1. Create a restore point **before** any file operations
2. Inform the user of the restore point ID
3. Perform the modification
4. Report completion with the revert command

Example prompt for AI:
> "I am about to modify the login page. Create a restore point first."

AI response:
```
[Restore point #1 created: "Modify login page"]
[Applying changes...]
[Done] To revert: say "restore to restore point #1"
```

### Technical Details

- **Snapshot mechanism**: Records `git rev-parse HEAD` (current commit SHA)
- **Uncommitted changes**: Auto-commits with `[RP-AUTO]` message before snapshot
- **Restore mechanism**: `git reset --hard <sha>` — reverts both HEAD and working tree
- **No data loss**: Current uncommitted changes are auto-committed before restore
- **Windows compatible**: UTF-8 output with GBK console fallback

### Requirements

- Git (auto-initializes if repository doesn't exist)
- Python 3.7+
- OpenClaw runtime (for AI agent integration)

### File Structure

```
code-restore-point/
├── SKILL.md                     # OpenClaw skill definition
├── README.md                    # Bilingual documentation (this file)
├── scripts/
│   └── create_restore_point.py  # Core script
└── code-restore-point.skill     # Packaged skill bundle
```

---

## 中文

### 简介

`code-restore-point` 是一个 OpenClaw 技能，在修改代码前记录当前 Git HEAD commit SHA，随时可通过 `git reset --hard` 一键回滚到该状态。

### 使用场景

- **批量重构**：重构大模块前创建快照，出问题立即恢复
- **风险实验**：试用新库或新模式，无需担心破坏代码
- **代码审查**：应用建议修改前先快照，安心试错
- **学习探索**：安全地修改不熟悉的代码库
- **配置修改**：修改共享配置前先备份，避免连锁破坏

### 核心功能

- **一键快照**：记录当前 HEAD commit SHA；未提交变更自动提交后记录
- **命名还原点**：每个快照附带备注，方便识别用途
- **即时回滚**：`git reset --hard` 到记录的 commit — 完整还原工作区
- **自动初始化**：非 Git 目录自动初始化
- **自动清理**：恢复后自动从索引移除，防止重复应用
- **孤儿清理**：清理指向已删除 commit 的过期记录

### 安装

#### 方式一：通过 GitHub Release 下载（推荐）

1. 从 [Releases](https://github.com/richard3153/code-restore-point/releases) 页面下载最新的 `.skill` 安装包
2. 将其放入 OpenClaw 技能目录：
   ```
   C:\Users\<你的用户名>\.qclaw\skills\code-restore-point\
   ```
3. 或通过 OpenClaw 技能安装命令安装

#### 方式二：手动克隆安装

```bash
git clone https://github.com/richard3153/code-restore-point.git %USERPROFILE%\.qclaw\skills\code-restore-point
```

### 使用方法

#### 修改代码前 — 创建还原点

```bash
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py create <备注>
```

示例：
```bash
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py create "重构用户认证模块"
```

#### 查看所有还原点

```bash
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py list
```

#### 恢复到指定还原点

```bash
# 按索引恢复（索引来自 list 命令输出）
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py restore 0
```

#### 恢复到最近一次还原点

```bash
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py restore-last
```

#### 清理孤儿记录

```bash
python %USERPROFILE%\.qclaw\skills\code-restore-point\scripts\create_restore_point.py cleanup
```

### AI 代理工作流

当用户要求修改代码时，AI 代理应：

1. **先创建还原点**（在任何文件操作之前）
2. **告知用户还原点编号**
3. 执行代码修改
4. 报告完成状态并提供回滚命令

AI 代理指令示例：
> "我要修改登录页面，先创建一个还原点"

AI 响应示例：
```
[还原点 #1 已创建："修改登录页面"]
[执行修改...]
[完成] 如需回滚，请说"恢复到还原点 #1"
```

### 技术细节

- **快照机制**：记录 `git rev-parse HEAD`（当前 commit SHA）
- **未提交变更**：快照前自动提交（消息 `[RP-AUTO]`）
- **还原机制**：`git reset --hard <sha>` — 同时还原 HEAD 和工作区
- **无数据丢失**：还原前自动提交当前未提交变更
- **Windows 兼容**：UTF-8 输出，GBK 控制台兼容

### 系统要求

- Git（仓库不存在时自动初始化）
- Python 3.7+
- OpenClaw 运行时（用于 AI 代理集成）

### 文件结构

```
code-restore-point/
├── SKILL.md                     # OpenClaw 技能定义文件
├── README.md                    # 双语说明文档
├── scripts/
│   └── create_restore_point.py  # 核心脚本
└── code-restore-point.skill     # 打包的技能包
```
