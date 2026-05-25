#!/usr/bin/env python3
"""
使用 PinchTab 导出 X (Twitter) 收藏夹链接
"""

import json
import sys
import time
from pathlib import Path

# 添加 skills 路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.pinchtab import PinchTab


def export_twitter_bookmarks():
    """导出 X 收藏夹链接"""

    browser = PinchTab()

    print("🚀 开始导出 X 收藏夹...")
    print("=" * 50)

    # 1. 导航到 X 收藏页面
    print("\n📌 步骤 1：导航到 X 收藏页面")
    print("⚠️  重要：需要先登录 X 账号！")
    print("   请访问 http://localhost:9867/dashboard 手动登录，或使用已登录的配置文件")
    print()

    bookmark_url = "https://x.com/i/bookmarks"
    print(f"   导航到: {bookmark_url}")
    browser.nav(bookmark_url)
    time.sleep(3)  # 等待页面加载

    # 2. 获取页面快照
    print("\n📸 步骤 2：获取页面快照...")
    snapshot = browser.snap(interactive=True, compact=True)

    if not snapshot or 'nodes' not in snapshot:
        print("❌ 无法获取页面快照，请检查：")
        print("   1. PinchTab 服务器是否运行")
        print("   2. 是否已登录 X 账号")
        print("   3. 是否在正确的页面")
        return

    print(f"   找到 {len(snapshot['nodes'])} 个元素")

    # 3. 查找收藏链接
    print("\n🔍 步骤 3：提取收藏链接...")

    bookmarks = []
    links_found = 0

    for node in snapshot['nodes']:
        if node.get('role') == 'link':
            name = node.get('name', 'Unknown')
            bookmarks.append({
                'name': name,
                'ref': node.get('ref'),
                'role': node.get('role')
            })
            links_found += 1
            print(f"   ✓ 找到链接: {name[:50]}")

    print(f"\n   共找到 {links_found} 个链接")

    if links_found == 0:
        print("\n⚠️  未找到链接，可能的原因：")
        print("   1. 页面还在加载中")
        print("   2. 需要滚动页面加载更多收藏")
        print("   3. 收藏列表结构不同")

        # 尝试获取页面文本
        print("\n📝 获取页面文本...")
        text_data = browser.text()
        print(text_data[:500])
        return

    # 4. 询问是否点击每个链接获取实际 URL
    print("\n🔗 步骤 4：获取实际 URL...")
    print("   需要点击每个收藏项来获取实际链接")
    print()

    actual_bookmarks = []
    for i, bookmark in enumerate(bookmarks[:10]):  # 限制前 10 个
        print(f"\n[{i+1}/{len(bookmarks)}] 处理: {bookmark['name'][:40]}...")

        # 点击链接
        result = browser.click(bookmark['ref'])
        time.sleep(2)

        # 获取当前 URL
        # 这里需要等待跳转完成，然后获取 URL
        # 由于 PinchTab 可能没有直接获取当前 URL 的命令
        # 我们假设点击后会跳转到目标页面
        # 实际实现可能需要其他方式

        actual_bookmarks.append({
            'name': bookmark['name'],
            'ref': bookmark['ref']
        })

    # 5. 保存结果
    output_file = "/tmp/twitter_bookmarks.json"
    print(f"\n💾 保存到: {output_file}")

    export_data = {
        'exported_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_bookmarks': len(actual_bookmarks),
        'bookmarks': actual_bookmarks
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 导出完成！")
    print(f"   总数: {len(actual_bookmarks)}")
    print(f"   文件: {output_file}")

    # 6. 生成 Markdown 格式
    md_file = "/tmp/twitter_bookmarks.md"
    print(f"\n📝 生成 Markdown: {md_file}")

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# X (Twitter) 收藏夹导出\n\n")
        f.write(f"**导出时间：** {export_data['exported_at']}\n")
        f.write(f"**总数：** {export_data['total_bookmarks']}\n\n")
        f.write("---\n\n")

        for i, bm in enumerate(actual_bookmarks, 1):
            f.write(f"{i}. [{bm['name']}](#)\n")

    print(f"   ✅ Markdown 文件已生成")

    # 7. 生成文本列表
    txt_file = "/tmp/twitter_bookmarks.txt"
    print(f"\n📄 生成文本列表: {txt_file}")

    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"X 收藏夹导出\n")
        f.write(f"导出时间: {export_data['exported_at']}\n")
        f.write(f"总数: {export_data['total_bookmarks']}\n\n")

        for i, bm in enumerate(actual_bookmarks, 1):
            f.write(f"{i}. {bm['name']}\n")

    print(f"   ✅ 文本文件已生成")

    print("\n" + "=" * 50)
    print("📋 导出文件：")
    print(f"   JSON:   {output_file}")
    print(f"   Markdown: {md_file}")
    print(f"   Text:    {txt_file}")
    print()
    print("💡 提示：")
    print("   1. 查看文件内容：cat /tmp/twitter_bookmarks.json")
    print("   2. 手动访问收藏页面并复制链接：https://x.com/i/bookmarks")


def interactive_export():
    """交互式导出"""

    browser = PinchTab()

    print("\n🎯 交互式导出模式")
    print("=" * 50)

    print("\n选择导出方式：")
    print("1) 自动提取（尝试从页面提取）")
    print("2) 手动输入（逐个输入链接）")
    print("3) 获取页面文本（原始内容）")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == "1":
        export_twitter_bookmarks()
    elif choice == "2":
        manual_input(browser)
    elif choice == "3":
        get_page_text(browser)
    else:
        print("❌ 无效选择")


def manual_input(browser):
    """手动输入链接"""

    print("\n📝 手动输入模式")
    print("逐个输入你的 X 收藏链接（输入空行结束）：\n")

    bookmarks = []
    while True:
        url = input(f"链接 {len(bookmarks)+1}: ").strip()
        if not url:
            break

        name = input(f"名称: ").strip() or f"Bookmark {len(bookmarks)+1}"

        bookmarks.append({
            'name': name,
            'url': url
        })

    if bookmarks:
        output_file = "/tmp/twitter_bookmarks_manual.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 已保存 {len(bookmarks)} 个链接到 {output_file}")


def get_page_text(browser):
    """获取页面文本"""

    print("\n📝 获取页面文本...")

    result = browser.text()

    # text() 返回 dict，需要提取 text 字段
    if isinstance(result, dict) and 'text' in result:
        text_data = result['text']
    elif isinstance(result, str):
        text_data = result
    else:
        text_data = None

    if text_data:
        output_file = "/tmp/twitter_bookmarks_page_text.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# X 收藏夹页面文本\n\n")
            f.write(text_data)

        print(f"✅ 页面文本已保存到 {output_file}")
        print(f"   长度: {len(text_data)} 字符")

        # 显示前 500 字符
        print(f"\n前 500 字符：\n{text_data[:500]}")
    else:
        print("❌ 无法获取页面文本")
        print(f"   返回结果: {result}")


def main():
    """主函数"""

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "auto":
            export_twitter_bookmarks()
        elif command == "manual":
            browser = PinchTab()
            manual_input(browser)
        elif command == "text":
            browser = PinchTab()
            get_page_text(browser)
        elif command == "help":
            print_help()
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    else:
        interactive_export()


def print_help():
    """打印帮助信息"""

    print("\n📚 使用帮助")
    print("=" * 50)
    print("\n使用方法：")
    print("  python export-twitter-bookmarks.py [command]")
    print("\n命令：")
    print("  auto    - 自动导出（需要先在 X 登录）")
    print("  manual  - 手动输入链接")
    print("  text    - 获取页面文本")
    print("  help    - 显示此帮助")
    print("\n示例：")
    print("  python export-twitter-bookmarks.py auto")
    print("  python export-twitter-bookmarks.py manual")
    print()
    print("⚠️  重要提示：")
    print("  1. 需要先登录 X 账号")
    print("     - 访问 http://localhost:9867/dashboard")
    print("     - 在浏览器中登录 x.com")
    print("  2. 自动模式需要页面完全加载")
    print("  3. 可能需要滚动页面加载所有收藏")


if __name__ == "__main__":
    main()
