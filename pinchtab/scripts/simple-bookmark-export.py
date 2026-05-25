#!/usr/bin/env python3
"""
简单的 X 收藏链接整理工具
通过命令行参数或文件读取链接
"""

import json
import sys
from pathlib import Path


def import_from_file(filepath):
    """从文件导入链接"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        bookmarks = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # 解析格式：名称|URL 或 URL
                if '|' in line:
                    parts = line.split('|', 1)
                    name = parts[0].strip()
                    url = parts[1].strip()
                else:
                    url = line
                    name = url
                
                if url.startswith('http'):
                    bookmarks.append({'name': name, 'url': url})
        
        return bookmarks
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return []


def save_bookmarks(bookmarks, format_type='all'):
    """保存收藏到多种格式"""

    if not bookmarks:
        print("❌ 没有收藏链接")
        return

    timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. JSON 格式
    json_file = "/tmp/twitter_bookmarks_simple.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'exported_at': timestamp,
            'total': len(bookmarks),
            'bookmarks': bookmarks
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON: {json_file}")

    if format_type in ['all', 'json']:
        # 2. Markdown 格式
        md_file = "/tmp/twitter_bookmarks_simple.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# X 收藏夹导出\n\n")
            f.write(f"**导出时间：** {timestamp}\n")
            f.write(f"**总数：** {len(bookmarks)}\n\n")
            f.write("---\n\n")
            
            for i, bm in enumerate(bookmarks, 1):
                f.write(f"{i}. [{bm['name']}]({bm['url']})\n")
        
        print(f"✅ Markdown: {md_file}")

    # 3. 纯文本格式
    txt_file = "/tmp/twitter_bookmarks_simple.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"X 收藏夹导出\n")
        f.write(f"导出时间: {timestamp}\n")
        f.write(f"总数: {len(bookmarks)}\n\n")
        
        for i, bm in enumerate(bookmarks, 1):
            f.write(f"{i}. {bm['name']}\n")
            f.write(f"   URL: {bm['url']}\n\n")
    
    print(f"✅ Text: {txt_file}")


def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("📚 使用说明")
        print("=" * 50)
        print("\n用法：")
        print("  python simple-bookmark-export.py <格式> [文件]")
        print("\n格式：")
        print("  all    - 所有格式 (JSON, Markdown, Text)")
        print("  json   - 仅 JSON")
        print("  md     - 仅 Markdown")
        print("  text   - 仅 Text")
        print("\n文件：")
        print("  可选，每行一个链接：名称|URL 或仅 URL")
        print("\n示例：")
        print("  python simple-bookmark-export.py all bookmarks.txt")
        print("  python simple-bookmark-export.py md")
        print("\n文件格式示例：")
        print("  My Favorite Tweet|https://x.com/user/status/123")
        print("  https://x.com/user/status/456")
        print()
        return

    format_type = sys.argv[1].lower()
    
    if len(sys.argv) > 2:
        # 从文件导入
        filepath = sys.argv[2]
        bookmarks = import_from_file(filepath)
        print(f"\n📂 从文件导入: {filepath}")
        print(f"✅ 导入 {len(bookmarks)} 个链接\n")
    else:
        # 示例收藏（如果用户想测试）
        bookmarks = [
            {
                'name': '示例收藏 1',
                'url': 'https://x.com/example1'
            },
            {
                'name': '示例收藏 2',
                'url': 'https://x.com/example2'
            }
        ]
        print("\n📝 使用示例数据（没有提供文件）")
        print(f"✅ 创建 {len(bookmarks)} 个示例链接\n")

    # 保存
    save_bookmarks(bookmarks, format_type)

    print("\n" + "=" * 50)
    print("📋 文件位置：")
    print(f"   JSON:   /tmp/twitter_bookmarks_simple.json")
    print(f"   Markdown: /tmp/twitter_bookmarks_simple.md")
    print(f"   Text:    /tmp/twitter_bookmarks_simple.txt")
    print()
    print("💡 使用示例：")
    print("   cat /tmp/twitter_bookmarks_simple.md | pbcopy  # 复制到剪贴板")
    print("   open /tmp/twitter_bookmarks_simple.md              # 在编辑器中打开")


if __name__ == "__main__":
    main()
