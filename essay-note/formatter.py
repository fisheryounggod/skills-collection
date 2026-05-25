#!/usr/bin/env python3
"""
随笔格式化器
将用户输入的随笔整理成格式化笔记
"""

import sys
import json

def format_essay(essay_data):
    """
    格式化随笔
    
    Args:
        essay_data: 收集器输出的数据
    
    Returns:
        markdown: 格式化的随笔内容
    """
    topic = essay_data.get("topic", "随笔")
    record_time = essay_data.get("record_time", "")
    core_ideas = essay_data.get("core_ideas", [])
    original = essay_data.get("original", "")
    tags = essay_data.get("tags", [])
    
    # 构建markdown
    md = f"# 💡 {topic}\n"
    md += f"记录时间：{record_time}\n\n"
    
    if core_ideas:
        md += "## 核心想法\n"
        for idea in core_ideas[:3]:  # 最多3句
            md += f"- {idea}\n"
        md += "\n"
    
    md += "## 原始记录\n"
    md += f"> {original}\n\n"
    
    if tags:
        md += "## 标签\n"
        md += ' '.join(tags) + '\n'
    
    return md

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python formatter.py '<essay_data_json>'"}))
        sys.exit(1)
    
    essay_data_json = sys.argv[1]
    
    try:
        essay_data = json.loads(essay_data_json)
    except:
        essay_data = {"topic": "随笔", "original": essay_data_json}
    
    md = format_essay(essay_data)
    print(md)

if __name__ == "__main__":
    main()
