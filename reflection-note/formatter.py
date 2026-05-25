#!/usr/bin/env python3
"""
反思格式化器
将用户的反思格式化
"""

import sys
import json
import re
from datetime import datetime

def format_reflection(reflection_data):
    """
    格式化反思
    
    Args:
        reflection_data: 收集器输出的数据
    
    Returns:
        markdown: 格式化的反思内容
    """
    reflection = reflection_data.get("reflection", "")
    time_str = reflection_data.get("time", "")
    
    # 构建markdown
    md = "## 反思\n"
    md += f"{reflection}\n"
    
    return md

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python formatter.py '<reflection_data_json>'"}))
        sys.exit(1)
    
    reflection_data_json = sys.argv[1]
    
    try:
        reflection_data = json.loads(reflection_data_json)
    except:
        reflection_data = {"reflection": reflection_data_json, "time": ""}
    
    md = format_reflection(reflection_data)
    print(md)

if __name__ == "__main__":
    main()
