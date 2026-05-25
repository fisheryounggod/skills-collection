#!/usr/bin/env python3
"""
格式化为飞书文档Markdown
将JSON格式的内容转换为飞书文档可用的Markdown格式
"""

import sys
import json
from datetime import datetime


def format_content(data):
    """格式化内容为Markdown"""
    platform = data.get("platform", "未知平台")
    author = data.get("author", "未知作者")
    title = data.get("title", "无标题")
    content = data.get("content", "")
    url = data.get("url", "")
    created_at = data.get("created_at", "")
    summary = data.get("summary", "")
    keywords = data.get("keywords", [])
    reason = data.get("reason", "")
    stats = data.get("stats", {})
    
    # 生成互动数据字符串
    stats_str = []
    if stats.get("likes"):
        stats_str.append(f"👍 {stats['likes']}")
    if stats.get("retweets"):
        stats_str.append(f"🔄 {stats['retweets']}")
    if stats.get("bookmarks"):
        stats_str.append(f"💾 {stats['bookmarks']}")
    if stats.get("views"):
        stats_str.append(f"👁️ {stats['views']}")
    
    stats_text = " | ".join(stats_str) if stats_str else "无"
    
    # 生成关键词字符串
    keywords_text = "、".join(keywords) if keywords else "无"
    
    # 生成Markdown
    markdown = f"""
### {title}

| 属性 | 内容 |
|:---|:---|
| **作者** | {author} |
| **平台** | {platform} |
| **发布时间** | {created_at} |
| **原文链接** | [查看原帖]({url}) |
| **互动数据** | {stats_text} |

**原文内容**：
> {content}

**AI 摘要**：
{summary}

**关键词**：{keywords_text}

**为什么收藏**：
{reason}

---
*收藏时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return markdown


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 append_to_feishu.py '<json_content>'"
        }))
        sys.exit(1)
    
    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"Invalid JSON: {e}"
        }))
        sys.exit(1)
    
    markdown = format_content(data)
    print(markdown)


if __name__ == "__main__":
    main()
