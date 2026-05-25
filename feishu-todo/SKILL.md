---
name: feishu-todo
description: |
  Read and write Feishu (飞书) Todos via API using OAuth user_access_token.
  Triggers when user says "飞书待办", "Feishu todo", etc.
created: 2026-04-23
tags: [飞书, feishu, todo, task, oauth]
---

# Feishu Todo Skill

## Authentication (OAuth User Token)

**⚠️ Critical**: Task API requires **user_access_token**, NOT tenant_access_token.

### Prerequisites
1. App must have `task:task:read` scope added in Feishu Open Platform
2. Redirect URL must be configured: `https://open.feishu.cn/connect/qr/oauth2/callback`
3. User must complete OAuth authorization

### Step 1: Get App Access Token
```bash
APP_TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a92714e0d2b8dbc4","app_secret":"Yi9VZBPGWlB17KBO1ks5mfKE5FQOUIiV"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['app_access_token'])")
```

### Step 2: Generate OAuth URL
```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a92714e0d2b8dbc4&redirect_uri=https%3A%2F%2Fopen.feishu.cn%2Fconnect%2Fqr%2Foauth2%2Fcallback&state=feishu_todo&scope=task%3Atask%3Aread%20task%3Atask
```

### Step 3: Exchange Code for User Token
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $APP_TOKEN" \
  -d '{"grant_type":"authorization_code","code":"YOUR_CODE"}'
```

Response contains:
- `access_token` — user access token (valid 2 hours)
- `refresh_token` — refresh token (valid 30 days)

### Step 4: Refresh Expired User Token
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $APP_TOKEN" \
  -d '{"grant_type":"refresh_token","refresh_token":"YOUR_REFRESH_TOKEN"}'
```

## Read Tasks

**Credentials file**: `~/.hermes/feishu_todo_creds.json`
```python
import json, urllib.request, datetime

with open('/home/yxf/.hermes/feishu_todo_creds.json') as f:
    creds = json.load(f)

req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/task/v2/tasks?page_size=50',
    headers={'Authorization': f'Bearer {creds["user_access_token"]}'}
)
with urllib.request.urlopen(req) as r:
    result = json.loads(r.read())

for t in result['data']['items']:
    status = "✅" if t['status'] == 'done' else "🔲"
    summary = t.get('summary', '(no title)')
    due = ""
    if t.get('due'):
        due_ts = int(t['due']['timestamp']) // 1000
        due = datetime.datetime.fromtimestamp(due_ts).strftime('%m-%d %H:%M')
    print(f"{status} [{t['task_id']}] {summary} {due}")
```

## Create Task

**Key field**: `summary` (NOT `title`) — the task title field in v2 API

```python
body = {
    "summary": "任务标题",
    "due": {
        "timestamp": str(int(datetime.datetime(2026, 4, 30, 18, 0).timestamp() * 1000)),
        "is_all_day": False
    },
    "origin": {"platform_i18n_name": {"zh_cn": "个人"}}
}

req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/task/v2/tasks',
    data=json.dumps(body).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {creds["user_access_token"]}'},
    method='POST'
)
with urllib.request.urlopen(req) as r:
    print(json.loads(r.read()))
```

## Complete Task
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/task/v2/tasks/{task_id}/complete" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN"
```

## Task Status Values
- `open` — 未完成
- `done` — 已完成

## Task Fields Reference
- `task_id` — short ID (e.g., "t100034")
- `guid` — global unique ID (e.g., "41ad23a8-4421-4de6-9a1a-cbf6dfc82212")
- `summary` — task title (use this, NOT `title`)
- `status` — `open` or `done`
- `due.timestamp` — Unix ms timestamp (convert: `//1000` for seconds)
- `origin.href.url` — source document link (for tasks from Feishu docs)
- `origin.platform_i18n_name.zh_cn` — origin source name (e.g., "云文档")

## Pitfalls
- **Code is one-time use**: Exchange immediately and save tokens to creds file
- **tenant_access_token does NOT work** for task API — must use user_access_token (OAuth)
- **Scope `task:task:read` must be added** in app settings, requires tenant admin approval
- **Refresh token**: Store in `~/.hermes/feishu_todo_creds.json`; re-authorize if expired
- **Task API v2 vs v1**: v2 returns `99991663` with tenant token; v1 returns `99991672` (more descriptive)
- **⚠️ refresh_token 30天过期**: 过期后只能重新授权，用户需再次扫码 → **推荐改用 Bitable 方案（见下文）**

---

## 替代方案：Bitable 任务看板（永久有效，无需用户 OAuth）

如果不想处理 Task API 的 OAuth 过期问题，可用**飞书 Bitable 代替 Task API**：
- ✅ tenant_access_token 永久有效（App 凭证，无需用户授权）
- ✅ 自动续期，不存在过期问题
- ✅ 支持自定义字段（状态、优先级、预计时长）
- ⚠️ 无飞书内置通知，依赖外部推送

凭证从 `~/.hermes/feishu_todo_creds.json` 读取（`app_id`, `app_secret`, `base_token`, `table_id` 字段）。

### 读取 Bitable 任务列表
```python
import json, urllib.request

creds_path = "/home/yxf/.hermes/feishu_todo_creds.json"
with open(creds_path) as f:
    creds = json.load(f)

# 1. 获取 tenant_access_token
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": creds["app_id"], "app_secret": creds["app_secret"]}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as r:
    tenant_token = json.loads(r.read())["tenant_access_token"]

# 2. 读取 Bitable 记录
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/bitable/v1/bitables/{creds['base_token']}/tables/{creds['table_id']}/records?page_size=100",
    headers={"Authorization": f"Bearer {tenant_token}"}
)
with urllib.request.urlopen(req) as r:
    records = json.loads(r.read())["data"]["items"]

for record in records:
    fields = record["fields"]
    title = fields.get("标题", fields.get("文献名称", ""))
    section = fields.get("阶段", "")
    status = "进行中" if "进行中" in str(section) else "待开始"
    print(f"[{status}] {title}")
```

### 已实现的完整脚本
`/home/yxf/scripts/work-planning-v2.py` — 读取 Bitable 文献表 + 市场数据，生成每日规划 Markdown。

### 何时用 Task API vs Bitable
| 场景 | 推荐方案 |
|------|---------|
| 需要飞书内置通知/到期提醒 | Task API（需处理 OAuth） |
| 持久化自动任务（cron 等） | **Bitable**（tenant token） |
| 用户手动管理任务 | 飞书 App 原生界面 |
