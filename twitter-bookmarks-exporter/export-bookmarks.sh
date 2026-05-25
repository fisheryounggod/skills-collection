#!/bin/bash

# Twitter Bookmarks Exporter
# 导出最新50条收藏并删除

set -e

# 设置 DevToolsActivePort 文件位置
export CDP_PORT_FILE="/tmp/chrome-debug/DevToolsActivePort"
CDP_SCRIPT="node /Users/mac/.claude/skills/chrome-cdp/scripts/cdp.mjs"
OUTPUT_DIR="/Users/mac/Downloads"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTPUT_DIR}/twitter_bookmarks_${TIMESTAMP}.csv"

echo "🔄 Twitter 书签导出工具"
echo "================================"

# 获取Chrome标签页
echo "📱 检查 Chrome 标签页..."
TABS=$($CDP_SCRIPT list 2>/dev/null | grep x.com/i/bookmarks || true)

if [ -z "$TABS" ]; then
    echo "🔓 打开 Twitter 书签页面..."
    TAB_OUTPUT=$($CDP_SCRIPT open https://x.com/i/bookmarks 2>&1)
    TAB_ID=$(echo "$TAB_OUTPUT" | grep -oE '[A-F0-9]{8}' | head -1)
    sleep 5
else
    TAB_ID=$(echo "$TABS" | grep -oE '[A-F0-9]{8}' | head -1)
fi

echo "📋 标签页 ID: $TAB_ID"

# 滚动加载推文
echo "⏳ 加载推文..."
for i in {1..15}; do
    $CDP_SCRIPT eval "$TAB_ID" 'window.scrollTo(0,document.body.scrollHeight)' >/dev/null 2>&1
    echo "  滚动 $i/15"
    sleep 2
done

# 检查推文数量
TWEET_COUNT=$($CDP_SCRIPT eval "$TAB_ID" 'document.querySelectorAll("article[data-testid=\"tweet\"]").length' 2>/dev/null | tr -d '\n')
echo "📊 发现 $TWEET_COUNT 条推文"

# 提取推文数据（限制50条）
echo "💾 提取数据..."
DATA=$($CDP_SCRIPT eval "$TAB_ID" '
const tweets = Array.from(document.querySelectorAll("article[data-testid=\"tweet\"]")).slice(0, 50);
JSON.stringify(tweets.map(t => {
  const te = t.querySelector("[data-testid=\"tweetText\"]");
  const le = t.querySelector("a[href*=\"/status/\"]");
  const hasMedia = t.querySelector("[data-testid=\"tweetPhoto\"]") || t.querySelector("[data-testid=\"videoPlayer\"]");
  return {
    title: (te?.innerText||"").substring(0,100).replace(/"/g, """),
    url: le ? "https://x.com" + le.getAttribute("href").split("?")[0] : "",
    summary: (te?.innerText||"").replace(/"/g, """).replace(/\n/g, " "),
    type: hasMedia ? "tweet_with_media" : "tweet"
  };
}))
' 2>/dev/null)

# 生成CSV
echo "title,url,summary,type" > "$OUTPUT_FILE"
echo "$DATA" | grep -oE '"title":"[^"]*","url":"[^"]*","summary":"[^"]*","type":"[^"]*"' | sed 's/\\"/"/g' | while read -r line; do
    title=$(echo "$line" | grep -oP '"title":"\K[^"]*')
    url=$(echo "$line" | grep -oP '"url":"\K[^"]*')
    summary=$(echo "$line" | grep -oP '"summary":"\K[^"]*')
    type=$(echo "$line" | grep -oP '"type":"\K[^"]*')
    echo "\"$title\",\"$url\",\"$summary\",\"$type\"" >> "$OUTPUT_FILE"
done

# 删除收藏
echo "🗑️ 删除收藏..."
DELETED=$($CDP_SCRIPT eval "$TAB_ID" '
(async () => {
  const tweets = document.querySelectorAll("article[data-testid=\"tweet\"]");
  let deleted = 0;
  for (let i = 0; i < Math.min(50, tweets.length); i++) {
    try {
      const removeBtn = tweets[i].querySelector("[data-testid=\"removeBookmark\"]");
      if (removeBtn) {
        removeBtn.click();
        deleted++;
        await new Promise(r => setTimeout(r, 300));
      }
    } catch (e) {}
  }
  return deleted;
})()
' 2>/dev/null | tr -d '\n')

echo ""
echo "✅ 完成！"
echo "📁 文件: $OUTPUT_FILE"
echo "📊 导出: $DELETED 条"
echo ""
