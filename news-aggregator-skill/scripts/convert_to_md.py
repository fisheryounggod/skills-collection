#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def format_item(item):
    """格式化单个条目为Markdown"""
    title = item.get('title', '无标题')
    url = item.get('url', '#')
    heat = item.get('heat', '')
    time = item.get('time', '')
    source = item.get('source', '')

    # 热度显示
    heat_str = f" 🔥 {heat}" if heat and heat not in ['', '0 points'] else ""

    # 时间显示
    time_str = f" ⏰ {time}" if time else ""

    return f"- [{title}]({url}){heat_str}{time_str} · *{source}*\n"

def format_section(section_name, items, limit=5):
    """格式化一个section"""
    if not items:
        return ""

    section_title = f"\n## {section_name}\n\n"
    section_items = "".join([format_item(item) for item in items[:limit]])
    return section_title + section_items

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_md.py <json_file>", file=sys.stderr)
        sys.exit(1)

    json_file = sys.argv[1]

    # 读取JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 生成简报
    today = datetime.now().strftime('%Y-%m-%d')
    weekday = datetime.now().strftime('%A')

    md_content = f"""# 📰 每日简报 — {today} {weekday}

> 由OpenClaw自动生成

---

## 🌍 全球扫描

"""

    # 按section组织内容
    sections = {
        "global_scan": ("全球扫描", 8),
        "hn_ai": ("Hacker News AI前沿", 10),
        "github_trending": ("GitHub趋势", 10)
    }

    for key, (title, limit) in sections.items():
        if key in data and data[key]:
            md_content += f"\n### {title}\n\n"
            for item in data[key][:limit]:
                md_content += format_item(item)
            md_content += "\n"

    # 输出
    print(md_content)

if __name__ == "__main__":
    main()
