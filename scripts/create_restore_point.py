#!/usr/bin/env python3
"""
创建代码还原点。
在代码修改前调用，记录当前工作区状态，并记录本次修改的说明。
"""
import json
import os
import subprocess
import sys
from datetime import datetime

WORKSPACE = os.environ.get("WORKSPACE_ROOT", os.getcwd())
RP_INDEX = os.path.join(WORKSPACE, ".restore-points.json")


def load_index():
    if os.path.exists(RP_INDEX):
        with open(RP_INDEX, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_index(index):
    with open(RP_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_git_root():
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=WORKSPACE, capture_output=True, text=True, timeout=10
        )
        if root.returncode == 0:
            return root.stdout.strip()
    except Exception:
        pass
    return WORKSPACE


def git_run(args, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 30)
    kwargs.setdefault("cwd", WORKSPACE)
    return subprocess.run(args, **kwargs)


def get_status_summary():
    """获取变更文件列表摘要"""
    result = git_run(["git", "status", "--porcelain"])
    if result.returncode != 0:
        return "无法获取变更状态"
    lines = [l for l in result.stdout.strip().split("\n") if l]
    if not lines:
        return "无变更"
    files = [l[3:] for l in lines]
    return f"变更文件 ({len(files)}): {', '.join(files[:5])}" + (" ..." if len(files) > 5 else "")


def create_restore_point(note):
    # 确保 git 仓库
    git_root = get_git_root()
    if git_run(["git", "rev-parse", "--git-dir"], cwd=git_root).returncode != 0:
        print("❌ 当前目录不是 Git 仓库，无法创建还原点", file=sys.stderr)
        sys.exit(1)

    status_before = get_status_summary()
    print(f"当前状态: {status_before}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 暂存所有变更（包括未跟踪文件）
    git_run(["git", "add", "-A"])

    # 创建 stash
    stash_msg = f"[RP-{timestamp}] {note}"
    result = git_run(["git", "stash", "push", "-m", stash_msg, "--include-untracked"])

    if result.returncode != 0:
        print(f"❌ git stash 失败: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # 从 stash message 提取 stash@{n}
    list_result = git_run(["git", "stash", "list"])
    stash_ref = None
    for line in list_result.stdout.strip().split("\n"):
        if stash_msg in line:
            # 提取 "stash@{n}" 格式
            import re
            m = re.search(r"(stash@\{\d+\})", line)
            if m:
                stash_ref = m.group(1)
                break

    if not stash_ref:
        # 回退 stash
        git_run(["git", "stash", "pop", "--index"])
        print("❌ 无法定位创建的 stash 引用", file=sys.stderr)
        sys.exit(1)

    entry = {
        "stash_ref": stash_ref,
        "timestamp": timestamp,
        "note": note,
        "status_summary": status_before,
        "workspace": WORKSPACE
    }

    index = load_index()
    index.append(entry)
    save_index(index)

    print(f"✅ 还原点已创建: [{len(index)}] {stash_ref}")
    print(f"   说明: {note}")
    print(f"   时间: {timestamp}")
    print(f"\n📝 下一步: 进行你的代码修改。完成修改后如需还原，运行:")
    print(f"   python \"{os.path.abspath(__file__)}\" restore {len(index) - 1}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python create_restore_point.py create <修改说明>  # 创建还原点")
        print("  python create_restore_point.py list              # 列出所有还原点")
        print("  python create_restore_point.py restore <索引>     # 还原到指定还原点")
        print("  python create_restore_point.py restore-last       # 还原到上一个还原点")
        print("  python create_restore_point.py cleanup            # 清理已应用的还原点")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "create":
        if len(sys.argv) < 3:
            print("❌ 请提供修改说明，例如: python create_restore_point.py create 修复登录bug", file=sys.stderr)
            sys.exit(1)
        note = " ".join(sys.argv[2:])
        create_restore_point(note)
    elif cmd == "list":
        list_restore_points()
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("❌ 请提供还原点索引，例如: python create_restore_point.py restore 0", file=sys.stderr)
            sys.exit(1)
        restore_restore_point(int(sys.argv[2]))
    elif cmd == "restore-last":
        restore_restore_point(-1)
    elif cmd == "cleanup":
        cleanup_applied()
    else:
        print(f"❌ 未知命令: {cmd}", file=sys.stderr)
        sys.exit(1)


def list_restore_points():
    index = load_index()
    if not index:
        print("📂 当前无还原点记录")
        return
    print(f"📂 代码还原点列表 (共 {len(index)} 个)\n")
    print(f"  {'索引':<6} {'时间戳':<18} {'说明':<30} {'Git引用'}")
    print(f"  {'-'*6} {'-'*18} {'-'*30} {'-'*20}")
    for i, rp in enumerate(index):
        note = rp["note"][:28] + ".." if len(rp["note"]) > 30 else rp["note"]
        print(f"  [{i}]    {rp['timestamp']:<18} {note:<30} {rp['stash_ref']}")
    print(f"\n恢复命令: python \"{os.path.abspath(__file__)}\" restore <索引>")


def restore_restore_point(idx):
    index = load_index()
    if not index:
        print("❌ 无还原点记录，无法还原", file=sys.stderr)
        sys.exit(1)
    if idx < 0:
        idx = len(index) - 1
    if idx < 0 or idx >= len(index):
        print(f"❌ 索引 {idx} 超出范围 (0-{len(index)-1})", file=sys.stderr)
        sys.exit(1)

    rp = index[idx]
    print(f"正在还原到还原点 [{idx}]: {rp['note']}")
    print(f"Git 引用: {rp['stash_ref']}")

    # 应用 stash
    result = git_run(["git", "stash", "pop", rp["stash_ref"]])
    if result.returncode != 0:
        print(f"⚠️  stash pop 失败，尝试 apply: {result.stderr}")
        result2 = git_run(["git", "stash", "apply", rp["stash_ref"]])
        if result2.returncode != 0:
            print(f"❌ 还原失败: {result2.stderr}", file=sys.stderr)
            sys.exit(1)

    # 从索引中移除
    index.pop(idx)
    save_index(index)

    print(f"✅ 已还原到 [{idx}]，当前工作区已恢复到 '{rp['note']}' 前的状态")
    print(f"   还原点记录已清除（防止重复应用）")


def cleanup_applied():
    """清理已不存在于 git stash list 中的条目"""
    index = load_index()
    if not index:
        print("📂 无还原点记录")
        return

    list_result = git_run(["git", "stash", "list"])
    existing = set()
    for line in list_result.stdout.strip().split("\n"):
        import re
        m = re.search(r"(stash@\{\d+\})", line)
        if m:
            existing.add(m.group(1))

    remaining = [rp for rp in index if rp["stash_ref"] in existing]
    removed = len(index) - len(remaining)

    if removed:
        save_index(remaining)
        print(f"✅ 已清理 {removed} 个孤立还原点记录")
    else:
        print("📂 无需清理，所有还原点记录均有效")


if __name__ == "__main__":
    main()
