#!/usr/bin/env python3
"""
创建代码还原点。
在代码修改前调用，记录当前 HEAD commit，记录修改说明。
后续可随时还原到该 commit 状态（git reset --hard）。
"""
import io, json, os, re, subprocess, sys
from datetime import datetime

# Windows GBK console 兼容
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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


def git_run(args, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("timeout", 30)
    kwargs.setdefault("cwd", WORKSPACE)
    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("errors", "replace")
    return subprocess.run(args, **kwargs)


def get_git_root():
    result = git_run(["git", "rev-parse", "--show-toplevel"])
    if result.returncode == 0:
        return result.stdout.strip()
    return WORKSPACE


def ensure_git_repo():
    """确保是 git 仓库"""
    result = git_run(["git", "rev-parse", "--git-dir"])
    if result.returncode != 0:
        print("当前目录不是 Git 仓库，无法创建还原点", file=sys.stderr)
        sys.exit(1)


def get_head():
    """获取当前 HEAD commit SHA"""
    result = git_run(["git", "rev-parse", "HEAD"])
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def get_status_summary():
    result = git_run(["git", "status", "--porcelain"])
    if result.returncode != 0:
        return "无法获取变更状态"
    lines = [l for l in result.stdout.strip().split("\n") if l]
    if not lines:
        return "无变更"
    files = [l[3:] for l in lines]
    return "变更文件 (" + str(len(files)) + "): " + ", ".join(files[:5]) + (" ..." if len(files) > 5 else "")


def entry_label(rp):
    return rp.get("head_sha", "")[:7]


def create_restore_point(note):
    ensure_git_repo()
    git_root = get_git_root()

    # 首次使用：自动初始化（仅当没有任何 commit 时）
    head = get_head()
    if not head:
        print("首次使用，自动初始化 Git 仓库...")
        git_run(["git", "add", "-A"])
        commit_result = git_run(["git", "commit", "-m", "[RP-INIT] Initial restore point base"])
        if commit_result.returncode != 0:
            print("Git 仓库初始化失败: " + commit_result.stderr, file=sys.stderr)
            sys.exit(1)
        head = get_head()
        print("Git 仓库已初始化")
    else:
        # 非首次：先将所有未提交变更提交（确保快照完整）
        status_result = git_run(["git", "status", "--porcelain"])
        if status_result.stdout.strip():
            print("检测到未提交变更，自动提交...")
            git_run(["git", "add", "-A"])
            msg = "[RP-AUTO] auto-save before restore point: " + note
            commit_result = git_run(["git", "commit", "-m", msg])
            if commit_result.returncode == 0:
                head = get_head()
                print("未提交变更已自动保存为 commit: " + head[:7])
            else:
                print("自动提交失败（不影响还原点创建）: " + commit_result.stderr)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status_before = get_status_summary()
    print("当前状态: " + status_before)

    entry = {
        "head_sha": head,
        "timestamp": timestamp,
        "note": note,
        "status_summary": status_before,
        "workspace": WORKSPACE
    }
    index = load_index()
    index.append(entry)
    save_index(index)
    idx = len(index)

    print("还原点已创建: [" + str(idx) + "] " + head[:7])
    print("说明: " + note)
    print("时间: " + timestamp)
    print("")
    print("下一步: 进行你的代码修改。完成后如需还原，运行:")
    print("  python \"" + os.path.abspath(__file__) + "\" restore " + str(idx - 1))


def list_restore_points():
    index = load_index()
    if not index:
        print("当前无还原点记录")
        return
    print("代码还原点列表 (共 " + str(len(index)) + " 个)")
    print("")
    print("  索引     时间戳               HEAD Commit  说明")
    print("  " + "-" * 6 + "  " + "-" * 18 + "  " + "-" * 11 + "  " + "-" * 30)
    for i, rp in enumerate(index):
        note = rp["note"]
        if len(note) > 30:
            note = note[:28] + ".."
        print("  [" + str(i) + "]    " + rp["timestamp"] + "  " + rp["head_sha"][:7] + "  " + note)
    print("")
    print("恢复命令: python \"" + os.path.abspath(__file__) + "\" restore <索引>")


def restore_restore_point(idx):
    index = load_index()
    if not index:
        print("无还原点记录，无法还原", file=sys.stderr)
        sys.exit(1)
    if idx < 0:
        idx = len(index) - 1
    if idx < 0 or idx >= len(index):
        print("索引 " + str(idx) + " 超出范围 (0-" + str(len(index) - 1) + ")", file=sys.stderr)
        sys.exit(1)

    rp = index[idx]
    head_sha = rp["head_sha"]
    print("正在还原到还原点 [" + str(idx) + "]: " + rp["note"])
    print("HEAD Commit: " + head_sha)

    # 先将当前所有变更提交（避免丢失）
    status_result = git_run(["git", "status", "--porcelain"])
    if status_result.stdout.strip():
        print("当前有未提交变更，自动保存...")
        git_run(["git", "add", "-A"])
        cur_head = get_head() or "(no head)"
        msg = "[RP-AUTO] auto-save at " + datetime.now().strftime("%Y%m%d_%H%M%S")
        git_run(["git", "commit", "-m", msg])

    # 还原到目标 commit
    result = git_run(["git", "reset", "--hard", head_sha])
    if result.returncode != 0:
        print("还原失败: " + result.stderr, file=sys.stderr)
        sys.exit(1)

    # 从索引中移除该还原点（防止重复应用）
    index.pop(idx)
    save_index(index)

    print("已还原到 [" + str(idx) + "]，工作区已恢复到 '" + rp["note"] + "' 前的状态")
    print("还原点记录已清除（防止重复还原）")


def cleanup_applied():
    """清理指向不存在 commit 的孤立条目"""
    index = load_index()
    if not index:
        print("无还原点记录")
        return

    remaining = []
    removed = 0
    for rp in index:
        commit_result = git_run(["git", "cat-file", "-t", rp["head_sha"]])
        if commit_result.returncode == 0:
            remaining.append(rp)
        else:
            removed += 1

    if removed:
        save_index(remaining)
        print("已清理 " + str(removed) + " 个孤立还原点记录")
    else:
        print("无需清理，所有还原点记录均有效")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python create_restore_point.py create <修改说明>  # 创建还原点")
        print("  python create_restore_point.py list              # 列出所有还原点")
        print("  python create_restore_point.py restore <索引>   # 还原到指定还原点")
        print("  python create_restore_point.py restore-last     # 还原到上一个还原点")
        print("  python create_restore_point.py cleanup           # 清理孤立记录")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 3:
            print("请提供修改说明，例如: create_restore_point.py create 修复登录bug", file=sys.stderr)
            sys.exit(1)
        create_restore_point(" ".join(sys.argv[2:]))
    elif cmd == "list":
        list_restore_points()
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("请提供还原点索引: create_restore_point.py restore 0", file=sys.stderr)
            sys.exit(1)
        restore_restore_point(int(sys.argv[2]))
    elif cmd == "restore-last":
        restore_restore_point(-1)
    elif cmd == "cleanup":
        cleanup_applied()
    else:
        print("未知命令: " + cmd, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
