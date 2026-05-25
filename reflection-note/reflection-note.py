#!/usr/bin/env python3
"""
反思记录助手主脚本（简化版）
收集、整理、输出反思内容（不自动保存）
"""

import sys
import json
import subprocess
from datetime import datetime

def main():
    # 1. 获取用户输入
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python reflection-note.py '<user_input>'"}))
        sys.exit(1)
    
    user_input = sys.argv[1]
    date = datetime.now().strftime('%Y-%m-%d')
    
    # 2. 收集反思内容
    collect_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/reflection-note/collector.py", user_input],
        capture_output=True,
        text=True
    )
    
    if collect_result.returncode != 0:
        print(json.dumps({"error": "收集失败", "details": collect_result.stderr}))
        sys.exit(1)
    
    reflection_data = json.loads(collect_result.stdout)
    
    # 3. 格式化反思
    format_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/reflection-note/formatter.py", json.dumps(reflection_data)],
        capture_output=True,
        text=True
    )
    
    if format_result.returncode != 0:
        print(json.dumps({"error": "格式化失败", "details": format_result.stderr}))
        sys.exit(1)
    
    md_reflection = format_result.stdout
    
    # 4. 输出格式化内容
    print("反思内容已格式化，准备写入日记...")
    print(md_reflection)
    
    # 5. 提示用户手动保存
    print(f"\n【提示】请手动将以下内容追加到今日日记的'## 反思'部分：")
    print(f"日记标题：{date} 日记")
    print(f"保存位置：https://my.feishu.cn/drive/folder/ZZMKfKN7Kl5WsYdUbRacokmjnwg")

if __name__ == "__main__":
    main()
