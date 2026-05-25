---
name: feedgrab-setup
description: |
  feedgrab 万能内容抓取工具安装与配置。触发词：「抓取内容」「内容采集」「feedgrab」「抓取脚本」「社交媒体内容」
  支持平台：微信公众号/知乎/小红书/X/Twitter/YouTube/B站/飞书/RSS/GitHub等17+平台。
created: 2026-04-23
tags: [内容抓取, feedgrab, 社交媒体, 爬虫, 内容采集]
---

# feedgrab 安装与配置指南

万能内容抓取工具，支持17+平台输出结构化 Markdown + YAML front matter。

## 平台支持

微信公众号、知乎、小红书、即刻、X/Twitter、YouTube、B站、飞书文档、RSS、Github、少数派、微博、百度、Discord、Telegram、豆瓣、Notion

## 安装状态

**macOS（Fisher）**：已安装在 `/opt/anaconda3/bin/feedgrab`，无需额外安装。

其他用户安装方式：
```bash
# uv 安装
uv pip install feedgrab loguru requests feedparser python-dotenv

# 或 pip 安装
pip install feedgrab loguru requests feedparser python-dotenv
```

## ⚠️ CLI 正确用法（高频踩坑点）

**正确方式：URL 作为位置参数，无子命令**
```bash
feedgrab "https://mp.weixin.qq.com/s/xxx"
feedgrab "https://www.xiaohongshu.com/explore/xxx"
```

**错误方式（skill 里老写法，切勿使用）**
```bash
feedgrab grab --url "..." --platform wechat   # ❌ 没有 grab 子命令
feedgrab fetch "..."                           # ❌ 没有 fetch 子命令
```

**正确输出控制**：
- `feedgrab` 默认只打印内容到 stdout，**不自动保存文件**
- 必须通过环境变量控制输出目录：
```bash
OUTPUT_DIR=~/hermes/feedgrab-output feedgrab "https://..."
# 文件保存位置：{OUTPUT_DIR}/{platform}/{作者名}_{日期}：标题.md
# 示例：~/hermes/feedgrab-output/mpweixin/计量经济圈_2026-04-29：xxx.md
```

## 输出路径配置

feedgrab 默认不保存文件到本地，只打印内容到 stdout。需通过环境变量控制输出目录：

```bash
# 输出到指定目录（推荐）
OUTPUT_DIR=~/hermes/feedgrab-output feedgrab "https://..."

# 文件保存位置：{OUTPUT_DIR}/{platform}/{作者名}_{日期}：标题.md
# 示例：~/hermes/feedgrab-output/mpweixin/计量经济圈_2026-04-29：xxx.md
```

也支持 Obsidian vault：
```bash
OBSIDIAN_VAULT=/path/to/vault feedgrab "https://..."
```

## 诊断命令
```bash
feedgrab doctor           # 检查所有平台状态
feedgrab doctor mpweixin  # 只检查微信公众号
feedgrab doctor xhs       # 只检查小红书
```

## 已知问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 微信公众号弹出验证码 | 需要登录微信会话 | `feedgrab login wechat` 扫码登录 |
| 小红书/X 抓取失败 | 需要登录 cookies | 手动登录后导出 cookies |
| 浏览器引擎缺失 | patchright/playwright 未装 | `uv pip install patchright && patchright install chromium` |
| `browserforge 初始化失败` | stealth headers 生成失败 | 可忽略，功能会降级，使用基础 header |

## 凭证文件位置（Linux/macOS）
- 配置文件：`~/.feedgrab/.env`
- Cookies/Sessions：`~/.feedgrab/sessions/`
