#!/usr/bin/env python3
"""
日记助手主脚本
收集、整理、保存日记
"""

import sys
import json
import subprocess
from datetime import datetime

def main():
    # 1. 获取用户输入
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python daily-journal.py '<user_input>'"}))
        sys.exit(1)
    
    user_input = sys.argv[1]
    date = datetime.now().strftime('%Y-%m-%d')
    
    # 2. 收集条目
    collect_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/daily-journal/input-collector.py", user_input],
        capture_output=True,
        text=True
    )
    
    if collect_result.returncode != 0:
        print(json.dumps({"error": "收集失败", "details": collect_result.stderr}))
        sys.exit(1)
    
    entries_data = json.loads(collect_result.stdout)
    entries = entries_data.get("entries", [])
    has_more = entries_data.get("has_more", False)
    
    if not entries:
        print(json.dumps({"message": "没有识别到日记内容"}))
        return
    
    # 3. 格式化
    format_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/daily-journal/formatter.py", json.dumps(entries), date],
        capture_output=True,
        text=True
    )
    
    if format_result.returncode != 0:
        print(json.dumps({"error": "格式化失败", "details": format_result.stderr}))
        sys.exit(1)
    
    md_content = format_result.stdout
    
    # 4. 保存到飞书
    save_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/daily-journal/save-to-wiki.py", md_content, date],
        capture_output=True,
        text=True
    )
    
    save_data = json.loads(save_result.stdout)
    
    # 5. 输出结果
    result = {
        "date": date,
        "entries_count": len(entries),
        "save_success": save_data.get("success", False),
        "message": "日记已保存" if save_data.get("success") else "保存失败"
    }
    
    if has_more:
        result["prompt"] = "还有要记的吗？"
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
