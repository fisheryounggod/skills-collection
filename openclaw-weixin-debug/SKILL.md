---
name: openclaw-weixin-debug
description: "OpenClaw WeChat (openclaw-weixin) plugin troubleshooting and API access. 诊断 token 状态、API 调用方式、session timeout 原因和重新登录流程。"
---

# openclaw-weixin Debug Skill

OpenClaw WeChat (openclaw-weixin) plugin troubleshooting and API access.

## 架构速查

| 组件 | 路径 |
|------|------|
| 插件目录 | `~/.openclaw/extensions/openclaw-weixin/` |
| 账号索引 | `~/.openclaw/openclaw-weixin/accounts.json` |
| 账号凭据 | `~/.openclaw/openclaw-weixin/accounts/{accountId}.json` |
| Context tokens | `~/.openclaw/openclaw-weixin/accounts/{accountId}.context-tokens.json` |
| ilink API base | `https://ilinkai.weixin.qq.com` |

## 关键文件格式

### 账号凭据文件 (`{accountId}.json`)
```json
{
  "token": "0774e2184c97@im.bot:...",
  "savedAt": "2026-04-04T16:32:57.799Z",
  "baseUrl": "https://ilinkai.weixin.qq.com",
  "userId": "o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat"
}
```

### Context tokens 文件 (`{accountId}.context-tokens.json`)
存储 userId → context_token 映射，发送消息时需要带上对应 userId 的 context_token。

## 诊断流程

### 1. 检查账号状态
```bash
openclaw channels list
```

### 2. 检查账号文件
```bash
cat ~/.openclaw/openclaw-weixin/accounts.json
ls ~/.openclaw/openclaw-weixin/accounts/
```

### 3. 常见错误

| errcode | 含义 | 解决方式 |
|---------|------|----------|
| -14, "session timeout" | Token 过期 | 重新扫码登录 |
| -1001 | 网络/连接错误 | 检查网关状态 |

### 4. 重启网关（解决临时连接问题）
```bash
openclaw gateway restart
```

### 5. 重新登录（Token 失效）
```bash
openclaw channels login --channel openclaw-weixin
```
会弹出二维码，用微信扫码授权。

## API 直接调用（仅供诊断）

发送消息需要的 Headers：
```
Content-Type: application/json
AuthorizationType: ilink_bot_token
Authorization: Bearer {token}  # 来自账号凭据文件
X-WECHAT-UIN: {随机 uint32 base64 编码}
iLink-App-Id: (留空)
iLink-App-ClientVersion: 0
```

**重要**：直接调用 ilink API 受限于 token 时效（通常 24-48h 内会 timeout）。通过 OpenClaw gateway 路由消息是更可靠的方式。

## 发送消息的正确方式

通过 OpenClaw gateway 的 `sendMessageWeixin` 函数发送，需要：
1. 有效的 token（未过期）
2. 有效的 context_token（从 context-tokens.json 读取）

Cron 任务推荐做法：
- 确保 gateway 长期运行（`openclaw gateway restart` 后台运行）
- 消息通过 OpenClaw 的 agent/cron 机制路由，而不是直接调 ilink API
- 定期检查 token 状态，发现 timeout 后重新 login

## 微信消息发送失败：TimerContext 根因

**错误**：`"Timeout context manager should be used inside a task"`

**来源**：`aiohttp/helpers.py:678`，aiohttp 3.13.5+ 的 `TimerContext.__enter__()` 在 event loop 无 current_task 时抛出。

### 两条发送路径

| 路径 | 条件 | 稳定性 |
|------|------|--------|
| **Live Adapter** | `openclaw-gateway` 运行中，`_LIVE_ADAPTERS` 非空 | ✅ 稳定 |
| **Standalone** | `_LIVE_ADAPTERS` 为空，每次创建新的 WeixinClient | ❌ TimerContext 错误 |

### 诊断

```bash
# 1. 检查 gateway 是否运行
ps aux | grep openclaw-gateway | grep -v grep

# 2. 检查 cron 任务真实投递状态（last_status:ok 不代表成功！）
python3 -c "
import json
with open('/home/yxf/.hermes/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    print(j['id'], j.get('last_status'), j.get('last_delivery_error'))
"

# 3. 直接测试发送
python3 -c "
import sys; sys.path.insert(0, '/home/yxf/.hermes/hermes-agent')
from tools.send_message_tool import send_message
result = send_message(target='weixin', message='测试')
print(result)
"
```

### 降级方案

**方案 A（推荐）**：保持 gateway 长期运行，发送走 live adapter 路径。
```bash
openclaw gateway restart && openclaw channels list
```

**方案 B**：cron 任务降级到 Telegram（稳定，已验证）。
- WeChat 发送失败时，target 改为 `telegram:yang fee`
- `send_message(action='list')` 可查看可用 target

**方案 C**：检查 `hermes-env.sh` 确保 WEIXIN_TOKEN 已 export 为真环境变量，而非 shell 变量。

⚠️ **重要**：`jobs.json` 的 `last_status: ok` 不代表消息投递成功！AI 可能报告"已发送"但实际静默失败。必须检查 `last_delivery_error` 是否为 null。

### 关键文件
- `gateway/platforms/weixin.py:1957` — `_LIVE_ADAPTERS` 判断，跳转 standalone
- `gateway/platforms/weixin.py:320-399` — `_cdn_upload`（触发超时的路径）
- `tools/send_message_tool.py:1343-1420` — `_send_weixin` 使用 `asyncio.run()` 子进程

## 红线

- 不要把 token 硬编码到脚本里——从账号文件动态读取
- context_token 和 token 需要配对使用
- Token 失效无法通过程序续期，必须重新扫码登录
- cron 任务不要依赖 `last_status: ok` 判断微信消息是否送达——必须同时检查 `last_delivery_error`
