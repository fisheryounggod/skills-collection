#!/usr/bin/env python3
"""
随笔助手主脚本
收集、整理、保存随笔
"""

import sys
import json
import subprocess
from datetime import datetime

def main():
    # 1. 获取用户输入
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python essay-note.py '<user_input>'"}))
        sys.exit(1)
    
    user_input = sys.argv[1]
    
    # 2. 收集（提取关键词和核心想法）
    collect_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/essay-note/collector.py", user_input],
        capture_output=True,
        text=True
    )
    
    if collect_result.returncode != 0:
        print(json.dumps({"error": "收集失败", "details": collect_result.stderr}))
        sys.exit(1)
    
    essay_data = json.loads(collect_result.stdout)
    
    # 3. 格式化
    format_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/essay-note/formatter.py", json.dumps(essay_data)],
        capture_output=True,
        text=True
    )
    
    if format_result.returncode != 0:
        print(json.dumps({"error": "格式化失败", "details": format_result.stderr}))
        sys.exit(1)
    
    md_content = format_result.stdout
    
    # 4. 保存到飞书
    save_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/essay-note/save-to-wiki.py", md_content],
        capture_output=True,
        text=True
    )
    
    save_data = json.loads(save_result.stdout)
    
    # 5. 输出结果
    result = {
        "topic": essay_data.get("topic", ""),
        "save_success": save_data.get("success", False),
        "message": "随笔已保存" if save_data.get("success") else "保存失败"
    }
    
    if save_data.get("success"):
        result["url"] = save_data.get("url", "")
        result["doc_id"] = save_data.get("doc_id", "")
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
