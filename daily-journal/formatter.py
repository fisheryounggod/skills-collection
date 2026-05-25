#!/usr/bin/env python3
"""
日记格式化器
将用户输入的条目组织成日记格式
"""

import sys
import json
import re
from datetime import datetime

def format_journal(entries, date=None):
    """
    格式化日记
    
    Args:
        entries: 条目列表
        date: 日期字符串（YYYY-MM-DD），默认今天
    
    Returns:
        markdown: 格式化的日记内容
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # 初始化各部分
    items = []
    feelings = []
    reflections = []
    
    for entry in entries:
        entry = entry.strip()
        
        # 简单的分类规则（基于关键词）
        if any(word in entry for word in ['感觉', '觉得', '难受', '开心', '放松', '累', '充实']):
            # 状态/感受
            if len(feelings) < 2:  # 最多2句
                feelings.append(entry)
        elif any(word in entry for word in ['认知', '理解', '学', '想', '反思', '意识']):
            # 反思
            reflections.append(entry)
        else:
            # 事项
            # 简洁化：去掉冗余词
            item = entry
            for word in ['今天', '我', '了']:
                item = item.replace(word, '')
            item = item.strip()
            if item:
                items.append(item)
    
    # 构建markdown
    md = f"# 📅 {date} 日记\n\n"
    
    if items:
        md += "## 今日事项\n"
        for item in items:
            md += f"- {item}\n"
        md += "\n"
    
    if feelings:
        md += "## 状态 & 感受\n"
        for feeling in feelings[:2]:  # 最多2句
            md += f"- {feeling}\n"
        md += "\n"
    
    if reflections:
        md += "## 反思\n"
        for reflection in reflections:
            md += f"- {reflection}\n"
    
    # 确保不超过300字
    content_only = md.replace('# 📅 ', '').replace(' 日记\n\n', '').replace('## 今日事项\n', '').replace('## 状态 & 感受\n', '').replace('## 反思\n', '').replace('- ', '').replace('\n', '')
    if len(content_only) > 300:
        # 截断
        md = md[:300] + "..."
    
    return md

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python formatter.py '<entries_json>' [date]"}))
        sys.exit(1)
    
    entries_json = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        entries = json.loads(entries_json)
    except:
        entries = [entries_json]  # 如果不是json数组，当作单个条目
    
    md = format_journal(entries, date)
    
    print(md)

if __name__ == "__main__":
    main()
