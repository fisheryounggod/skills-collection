---
name: weread-utils
description: 微信读书工具集成经验 — Cookie配置、已知bug、快速命令
---
# weread-utils

微信读书工具集成的经验记录。

## Cookie 配置
- Cookie 文件位置：`~/.config/weread/cookies.json`
- Cookie 有效期有限，过期后 API 可能返回 `errcode -2013`、401、未登录或 invalid cookie；2026-05-10 实测当前 Cookie 已过期
- 不要把 Cookie 原文打印给用户、写入 Skill 文档或提交到仓库

## 已知 Bug
`weread-import` 源码字段名拼错：
- 错误：`createdTime`
- 正确：`createTime`（无字母 d）
- 影响：`getBookshelf`、`getBooksStat` 等函数
- 绕过方案：直接调用时用正确字段名

## 快速命令
```bash
# 检查全局 CLI
which weread-import
weread-import --version

# 检查 Cookie 文件（只打印键名，不打印值）
cat ~/.config/weread/cookies.json | jq 'keys'

# Hermes 每日导出脚本：导出到 ~/hermes/weread/YYYY-MM-DD/
/Users/mac/.hermes/scripts/weread-channel.sh

# weread-import 也支持直接导出
weread-import --all --limit 5 --output /tmp/weread-test
```

## 环境限制
- WSL 无 Display，无法使用 Chrome 调试模式（方案 B 不可行）
- `weread-cli` npm 包是空壳，无实际功能
- Cookie 方式是唯一可行方案

## 中国金融数据抓取（Chrome 代理模式）

当 akshare / curl / Python requests 无法直接访问中国金融网站（东方财富、同花顺等）时，使用 Chrome 作为代理：

**典型场景**：
- `akshare` → `ProxyError: Unable to connect to proxy`（东方财富 push2.eastmoney.com 被直连拒绝）
- `curl` → 无输出或 `Forbidden`（新浪/东财 API 需要浏览器 UA 或登录态）
- `curl https://hq.sinajs.cn/list=sh000001` → `Forbidden`
- Chrome 浏览器 → 正常访问

**工作流**：
1. 用户在 Chrome 中手动打开目标页面（如 `https://data.eastmoney.com/zjlx/detail.html`）
2. 等待页面完全加载（数据渲染完成）
3. 告知 agent "好了"
4. Agent 用 baoyu-fetch 通过 CDP 抓取已渲染的页面：
```bash
cd /Users/mac/.hermes/skills/openclaw-imports/baoyu-url-to-markdown
bun scripts/vendor/baoyu-fetch/src/cli.ts "<url>" \
  --output /tmp/finance.md --wait-for force --timeout 600000
```

**Fisher 的 Chrome CDP 端点**：
- 调试端口：`http://127.0.0.1:60267`
- Chrome profile：`/Users/mac/Library/Application Support/baoyu-skills/chrome-profile`
- 复用已有 Chrome 时，baoyu-fetch 自动使用该端口，无需额外参数
