import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import json

async def search_mankiw():
    async with async_playwright() as p:
        # 使用已保存的会话（不需要 storage_state，因为 browser_profile 已包含）
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="/Users/mac/.zlibrary/browser_profile",
            headless=False
        )
        
        page = await browser.new_page()
        
        # 访问 Z-Library 搜索页面
        search_query = urllib.parse.quote("Mankiw Macroeconomics")
        await page.goto(f"https://zh.zlib.li/search/{search_query}")
        
        # 等待页面加载
        await page.wait_for_timeout(8000)
        
        # 获取页面内容
        content = await page.content()
        
        # 保存页面内容用于分析
        with open("/Users/mac/claudecode/曼昆宏观经济学-slides-20260326/search_results.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        # 尝试提取书籍信息
        books = await page.query_selector_all("[data-book-id]")
        
        results = []
        for i, book in enumerate(books[:10]):
            try:
                # 尝试不同的选择器
                title_elem = await book.query_selector(".book__title")
                author_elem = await book.query_selector(".book__authors")
                
                if title_elem:
                    title = await title_elem.inner_text()
                    author = await author_elem.inner_text() if author_elem else "Unknown"
                    
                    # 获取链接
                    link_elem = await book.query_selector("a")
                    if link_elem:
                        href = await link_elem.get_attribute("href")
                        
                        results.append({
                            "index": i + 1,
                            "title": title.strip(),
                            "author": author.strip(),
                            "url": f"https://zh.zlib.li{href}" if href and not href.startswith("http") else href
                        })
            except Exception as e:
                print(f"Error processing book {i}: {e}")
                continue
        
        await browser.close()
        
        return results

if __name__ == "__main__":
    results = asyncio.run(search_mankiw())
    print(f"\n找到 {len(results)} 本相关书籍：\n")
    for r in results:
        print(f"{r['index']}. {r['title']}")
        print(f"   作者: {r['author']}")
        print(f"   链接: {r['url']}")
        print()
