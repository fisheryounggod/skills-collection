---
name: twitter-bookmarks-exporter
description: Export latest 50 Twitter/X bookmarks to CSV and delete them
---

# Twitter Bookmarks Exporter

自动导出 Twitter/X 最新 50 条收藏为 CSV，并从收藏中删除。

## 使用方法

```bash
# 导出最新50条收藏并删除
./export-bookmarks.sh
```

## 输出

- CSV 文件: `twitter_bookmarks_YYYYMMDD_HHMMSS.csv`
- 字段: title, url, summary, type
- 自动删除已导出的收藏

## 要求

- Chrome 已开启远程调试 (`chrome://inspect/#remote-debugging`)
- 已登录 Twitter/X
