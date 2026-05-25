#!/usr/bin/env python3
"""
Hermes Downloads Sync
1. 文件检查归档：确保根目录干净，杂散文件移入对应分类
2. 同步到 GitHub fisheryounggod/hermes
Token: HERMES_GITHUB_TOKEN env var
"""
import argparse
import base64
import hashlib
import os
import re
import shutil
import sys
import time

import requests

DOWNLOAD_BASE = os.path.expanduser("~/hermes")
TOKEN = os.environ.get("HERMES_GITHUB_TOKEN", "")
OWNER, REPO = "fisheryounggod", "hermes"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "hermes-sync-python/1.0",
}

# 分类规则：文件名关键词 → 目标文件夹。
# 注意：按 dict 顺序匹配；宽泛关键词放后面，避免抢占更具体分类。
CLASSIFY_RULES = {
    "travel":     ["hangzhou", "shanghai", "trip", "travel", "出行"],
    "cards_raw":  ["infograph", "raw-card", "card-raw", "原始卡片"],
    "cards":      ["card", "卡片"],
    "finance":    ["finance", "quant", "量化", "投资", "stock", "金融", "定投", "dca"],
    "system":     ["system", "系统", "工程", "guide"],
    "scripts":    [".py", ".sh", ".js"],
    "reports":    ["analysis", "report", "分析", "报告"],
    "work":       ["work", "工作"],
    "learning":   ["learning", "学习", "英语", "英语学习"],
    "research":   ["research", "paper", "研究", "论文"],
    "video":      ["video", "视频", "mp4"],
    "books":      ["pdf", "epub", "dmg", "book"],
}

# 允许停留在根目录的文件
ROOT_ALLOWED = {"index.html", "TASK.md"}

# 不上传的目录/文件模式
EXCLUDE_DIRS = {"archived", ".git", "__pycache__", "node_modules", ".claude", "$RECYCLE.BIN", ".Trash"}
EXCLUDE_EXTS = {".mp4", ".dmg", ".pdf", ".zip", ".epub", ".docx", ".xlsx"}
EXCLUDE_NAMES = {"Thumbs.db", "desktop.ini", ".DS_Store"}
MAX_FILE_SIZE_MB = 10


def get_token():
    """Read GitHub token from env, falling back to ~/.profile for cron contexts."""
    if TOKEN:
        return TOKEN

    profile_path = os.path.expanduser("~/.profile")
    if not os.path.exists(profile_path):
        return ""

    token_re = re.compile(r"^(?:export\s+)?HERMES_GITHUB_TOKEN=(.*)$")
    with open(profile_path, encoding="utf-8") as f:
        for line in f:
            match = token_re.match(line.strip())
            if not match:
                continue
            val = match.group(1).strip()
            # Strip inline comment only when the value is not quoted.
            if val and val[0] not in {'\"', "'"}:
                val = val.split(" #", 1)[0].strip()
            return val.strip('"').strip("'")
    return ""


def classify_filename(fname):
    """根据文件名关键词返回分类目录，None 表示留在根目录。"""
    fname_lower = fname.lower()
    for category, keywords in CLASSIFY_RULES.items():
        for kw in keywords:
            if kw.lower() in fname_lower:
                return category
    return None


def should_upload(fname, fpath):
    """判断文件是否应上传；大体积二进制/Office 文件跳过。"""
    ext = os.path.splitext(fname)[1].lower()
    size_mb = os.path.getsize(fpath) / 1024 / 1024
    if ext in EXCLUDE_EXTS and size_mb > MAX_FILE_SIZE_MB:
        return False, f"large {ext} file {size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB"
    return True, ""


def scan_and_archive(dry_run=False):
    """检查根目录，杂散文件移入对应分类。dry-run 时只报告，不移动/删除。"""
    actions = []
    if not os.path.isdir(DOWNLOAD_BASE):
        actions.append(f"  ❌ 同步目录不存在: {DOWNLOAD_BASE}")
        return actions

    root_files = os.listdir(DOWNLOAD_BASE)
    for fname in root_files:
        fpath = os.path.join(DOWNLOAD_BASE, fname)

        # 跳过目录和允许的根目录文件
        if os.path.isdir(fpath) or fname in ROOT_ALLOWED:
            continue

        # 跳过隐藏文件、排除目录和排除文件名
        if fname.startswith('.') or fname in EXCLUDE_DIRS or fname in EXCLUDE_NAMES:
            continue

        category = classify_filename(fname)
        if category:
            dest_dir = os.path.join(DOWNLOAD_BASE, category)
            dest_name = fname
            dest_path = os.path.join(dest_dir, dest_name)

            # 如果目标已有同名文件，大小相同则删除根目录副本；大小不同则加时间戳避免覆盖。
            if os.path.exists(dest_path):
                if os.path.getsize(fpath) == os.path.getsize(dest_path):
                    action = f"  ⏭️  跳过（已存在）: {fname} → {category}/"
                    actions.append(action if not dry_run else f"  [dry-run] {action.strip()}；将删除根目录重复副本")
                    if not dry_run:
                        os.remove(fpath)
                    continue
                name, ext = os.path.splitext(fname)
                dest_name = f"{name}_{int(time.time())}{ext}"
                dest_path = os.path.join(dest_dir, dest_name)

            action = f"  📦 归档: {fname} → {category}/{dest_name if dest_name != fname else ''}".rstrip()
            actions.append(action if not dry_run else f"  [dry-run] {action.strip()}")
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(fpath, dest_path)
        else:
            actions.append(f"  ⚠️  无法分类（需手动处理）: {fname}")

    return actions


def list_local_files():
    """递归列出 hermes 下所有应上传文件，并返回被规则跳过的文件。"""
    files, excluded = [], []
    for root, dirs, filenames in os.walk(DOWNLOAD_BASE):
        # 原地修改 dirs，阻止遍历排除目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in filenames:
            if fname.startswith('.') or fname in EXCLUDE_NAMES:
                continue
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, DOWNLOAD_BASE)
            ok, reason = should_upload(fname, fpath)
            if not ok:
                excluded.append((rel_path, reason))
                continue
            files.append(rel_path)
    return files, excluded


def get_remote_sha(rel_path, retries=3):
    """Get SHA for a single file from GitHub with retry on transient network errors."""
    tok = get_token()
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{API}/contents/{requests.utils.quote(rel_path, safe='/')}",
                auth=(OWNER, tok), headers=HEADERS, timeout=30
            )
            if r.status_code == 200:
                return r.json().get("sha")
            return None
        except requests.exceptions.RequestException as e:
            last_err = str(e)[:120]
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    print(f"  ⚠️  SHA 查询失败: {rel_path} ({last_err})")
    return None


def fetch_remote_tree():
    """Fetch remote git tree once so unchanged files can be skipped quickly."""
    tok = get_token()
    try:
        r = requests.get(
            f"{API}/git/trees/main?recursive=1",
            auth=(OWNER, tok), headers=HEADERS, timeout=60
        )
        if r.status_code == 200:
            return {item["path"]: item["sha"] for item in r.json().get("tree", []) if item.get("type") == "blob"}
        print(f"  ⚠️  远程文件树获取失败 (HTTP {r.status_code})，回退逐文件上传")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  远程文件树获取失败: {str(e)[:120]}，回退逐文件上传")
    return {}


def local_blob_sha(rel_path):
    """Compute git blob SHA for a local file, matching GitHub tree item sha."""
    fpath = os.path.join(DOWNLOAD_BASE, rel_path)
    with open(fpath, "rb") as f:
        content = f.read()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def upload_file(rel_path, retries=2):
    """上传单个文件到 GitHub。"""
    fpath = os.path.join(DOWNLOAD_BASE, rel_path)
    if not os.path.exists(fpath):
        return False, "local file not found"

    ok, reason = should_upload(os.path.basename(rel_path), fpath)
    if not ok:
        return False, f"skipped: {reason}"

    tok = get_token()
    with open(fpath, "rb") as f:
        content = f.read()
    encoded = base64.b64encode(content).decode()

    sha = get_remote_sha(rel_path)
    data = {"message": f"sync: {rel_path}", "content": encoded}
    if sha:
        data["sha"] = sha

    # Use longer timeout for larger files
    size_mb = len(content) / 1024 / 1024
    timeout = 120 if size_mb > 0.1 else 30

    last_err = None
    for attempt in range(retries + 1):
        try:
            r = requests.put(
                f"{API}/contents/{requests.utils.quote(rel_path, safe='/')}",
                auth=(OWNER, tok), headers=HEADERS, json=data, timeout=timeout
            )
            return r.status_code in (200, 201), r.status_code
        except requests.exceptions.RequestException as e:
            last_err = str(e)[:80]
            if attempt < retries:
                time.sleep(2 ** attempt)
    return False, f"timeout after {retries + 1} attempts: {last_err}"


def upload_index_html(remote_tree=None, dry_run=False):
    """上传动态版 index.html；未变化时跳过，dry-run 时只报告。"""
    rel_path = "index.html"
    index_path = os.path.join(DOWNLOAD_BASE, rel_path)
    if not os.path.exists(index_path):
        print("  ⚠️  本地无 index.html，跳过")
        return True, "missing"

    if remote_tree and remote_tree.get(rel_path) == local_blob_sha(rel_path):
        return True, "unchanged"

    if dry_run:
        return True, "would_update"

    tok = get_token()
    with open(index_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    sha = get_remote_sha(rel_path)
    data = {"message": "chore: update index.html", "content": encoded}
    if sha:
        data["sha"] = sha

    r = requests.put(
        f"{API}/contents/index.html",
        auth=(OWNER, tok), headers=HEADERS, json=data, timeout=30
    )
    return r.status_code in (200, 201), r.status_code


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Sync ~/hermes to GitHub via Contents API")
    parser.add_argument("--dry-run", action="store_true", help="show archive/upload plan without moving files or writing GitHub")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    token = get_token()
    if not token:
        print("ERROR: No HERMES_GITHUB_TOKEN found")
        sys.exit(1)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"=== Hermes 同步开始 ({mode}) ===\n")

    # Step 1: 归档检查
    print("【Step 1】文件检查与归档")
    archive_actions = scan_and_archive(dry_run=args.dry_run)
    if archive_actions:
        for a in archive_actions:
            print(a)
    else:
        print("  ✅ 根目录干净，无需归档")
    print()

    # Step 2: 同步文件
    print("【Step 2】同步到 GitHub")
    local_files, excluded_files = list_local_files()
    print(f"  本地可上传文件数: {len(local_files)}")
    if excluded_files:
        print(f"  规则跳过文件数: {len(excluded_files)}")
        for rel_path, reason in excluded_files[:20]:
            print(f"  🚫 {rel_path} ({reason})")
        if len(excluded_files) > 20:
            print(f"  ... 另有 {len(excluded_files) - 20} 个跳过文件")

    remote_tree = fetch_remote_tree()
    uploaded, skipped, failed = [], [], []
    for rel_path in local_files:
        if remote_tree and remote_tree.get(rel_path) == local_blob_sha(rel_path):
            skipped.append(rel_path)
            print(f"  ⏭️  {rel_path} (unchanged)")
            continue

        if args.dry_run:
            uploaded.append(rel_path)
            print(f"  [dry-run] ⬆️  would upload: {rel_path}")
            continue

        ok, code = upload_file(rel_path)
        if ok:
            uploaded.append(rel_path)
            print(f"  ✅ {rel_path}")
        else:
            failed.append((rel_path, code))
            print(f"  ❌ {rel_path} ({code})")

    # Step 3: 更新 index.html
    print("\n【Step 3】更新 index.html")
    idx_ok, idx_code = upload_index_html(remote_tree=remote_tree, dry_run=args.dry_run)
    if idx_ok and idx_code == "unchanged":
        print("  ⏭️  index.html 未变化，跳过")
    elif idx_ok and idx_code == "would_update":
        print("  [dry-run] ⬆️  would update index.html")
    elif idx_ok:
        print("  ✅ index.html 已更新")
    else:
        print(f"  ❌ index.html 更新失败 (HTTP {idx_code})")

    print(f"\n=== 同步完成 ({mode}) ===")
    upload_label = "将上传" if args.dry_run else "上传"
    print(f"  {upload_label}: {len(uploaded)} | 跳过: {len(skipped)} | 规则排除: {len(excluded_files)} | 失败: {len(failed)}")

    summary = (
        f"✅ Hermes 同步完成 ({mode})\n\n"
        f"📦 {upload_label}: {len(uploaded)} 文件\n"
        f"⏭️ 跳过: {len(skipped)} 个未变化文件\n"
        f"🚫 规则排除: {len(excluded_files)} 文件\n"
        f"❌ 失败: {len(failed)} 文件\n"
        f"📄 index.html: {'⏭️ 未变化' if idx_code == 'unchanged' else ('🧪 dry-run 将更新' if idx_code == 'would_update' else ('✅ 已更新' if idx_ok else '❌ 更新失败'))}"
    )
    if archive_actions:
        summary += "\n归档操作:\n" + "\n".join(archive_actions[:5])
    if failed:
        summary += "\n失败文件:\n" + "\n".join(f for f, _ in failed)

    print(summary)


if __name__ == "__main__":
    main()
