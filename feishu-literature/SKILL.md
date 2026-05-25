---
name: feishu-literature
description: |
  飞书文献管理系统。默认对 Base「文献研究」（O26ebCYPRa56Nvsy48icxkMXn6O）进行文献管理。
  触发：文献管理、查文献、找论文、看进度、添加文献、更新阅读状态
created: 2026-04-23
tags: [飞书, feishu, literature, base, bitable, 文献管理]
---

# Feishu Literature Management Skill

## Base Info

- Base Token: 读 `~/.hermes/feishu_literature_creds.json` → `base_token`
- Base URL: https://my.feishu.cn/base/O26ebCYPRa56Nvsy48icxkMXn6O
- Credentials: `~/.hermes/feishu_todo_creds.json` → `user_access_token`

### Tables

| 表名 | Table ID | 用途 |
|------|----------|------|
| From OpenAlex | `tblQOcl30tUp0lmN` | OpenAlex 导入的论文，含摘要/方法/发现 |
| 文献清单 | `tblaWA2qpMhkw2Po` | 论文清单，含阶段/重要性/状态/时间 |
| 阅读进度 | `tbl9Teu90g7ADBly` | 阅读记录，含日期/时长/核心发现/笔记 |
| 阶段管理 | `tblbmcXm5SfyF36Z` | 研究阶段管理，含起止/文献数/检查清单 |
| 资本流动波动分类 | `tblmXCBlXArf9Amx` | 资本流动波动研究分类，含5大顶层类+14个子类 |
| 资本流动实证分析 | `tblSugmyUAXTcmPd` | 资本流动实证文献模板，含Agents/Behavior/Constraint/B2C字段 |

## Critical: Record Insertion Uses Field NAMES, Not Field IDs

**Bug/workaround discovered 2026-04-23:**

Record insertion (`POST /tables/{id}/records`) accepts **field names as keys**, NOT field IDs:
```python
# ✅ CORRECT — use field names
body = {"fields": {"分类编号": "A", "分类名称": "计量方法论", ...}}

# ❌ WRONG — field IDs return FieldNameNotFound (code 1254045)
body = {"fields": {"fldH2yGFsI": "A", "fldv8QLrKD": "计量方法论", ...}}
```

If you get `FieldNameNotFound` on record insert → switch from field IDs to field names.

## Field Creation API Format

Field creation (`POST /tables/{id}/fields`) uses a **flat structure** — no `field` wrapper:
```python
# ✅ Correct format
{"field_name": "分类编号", "type": 1}   # text field
{"field_name": "研究阶段", "type": 3}   # single-select field

# ❌ Wrong: nested wrapper (this causes 400 Bad Request)
{"field": {"field_name": "分类编号", "type": 1}}
```

**Table creation** does use a wrapper:
```python
{"table": {"name": "新表名"}}   # table creation
```

## Number Field Type: Year Must Be Integer

When inserting records, **year/number fields must be Python int, not string**:
```python
# ✅ Correct
"年份": 2012

# ❌ Wrong: NumberFieldConvFail
"年份": "2012"
```

## Token 续期（user_access_token 过期时）

**症状：** API 调用返回 `code: 20005` 或 `code: 99991663`

**检查方式：**
```python
import urllib.request, json
with open('/Users/mac/.hermes/feishu_todo_creds.json') as f:
    token = json.load(f)['user_access_token']
req = urllib.request.Request('https://open.feishu.cn/open-apis/authen/v1/user_info')
req.add_header('Authorization', f'Bearer {token}')
with urllib.request.urlopen(req, timeout=10) as r:
    print(json.loads(r.read()))
# code 20005 = invalid access token
```

**刷新失败时的重新授权流程：**

1. **打开授权页面**（需浏览器交互）：
   ```
   https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a910623283f8dbcb&redirect_uri=http%3A%2F%2Flocalhost&state=test&scope=bitable%3Aapp%3Atoken%3Auser
   ```

2. 浏览器完成飞书授权后，URL 会跳转到 `http://localhost/?code=xxx&state=test`

3. 用 code 换取 token：
   ```python
   # 需要先获取 app_access_token
   import urllib.request, json
   
   # Step 1: app_access_token
   app_req = urllib.request.Request(
       'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal',
       data=json.dumps({"app_id": "cli_a910623283f8dbcb", "app_secret": "<需要用户提供>"}).encode(),
       method='POST'
   )
   app_req.add_header('Content-Type', 'application/json')
   with urllib.request.urlopen(app_req, timeout=10) as r:
       app_token = json.loads(r.read())['app_access_token']
   
   # Step 2: 用 code 换 user_access_token
   code = "<从URL中提取的code>"
   user_req = urllib.request.Request(
       'https://open.feishu.cn/open-apis/authen/v1/oidc/access_token',
       data=json.dumps({"grant_type": "authorization_code", "code": code}).encode(),
       method='POST'
   )
   user_req.add_header('Content-Type', 'application/json')
   user_req.add_header('Authorization', f'Bearer {app_token}')
   with urllib.request.urlopen(user_req, timeout=10) as r:
       result = json.loads(r.read())
       new_token = result['data']['access_token']
       new_refresh = result['data']['refresh_token']
   
   # Step 3: 保存新token
   with open('/Users/mac/.hermes/feishu_todo_creds.json', 'w') as f:
       json.dump({'user_access_token': new_token, 'refresh_token': new_refresh, 'saved_at': __import__('time').time()}, f)
   ```

**注意：** 需要用户提供 `app_secret`（在飞书开放平台 → 应用详情 → 凭证与基础信息中）

## IMA Note Credentials

IMA API key was refreshed on 2026-04-23. Current credentials:
- Client ID: `405b7850dbd1590c9f269ff31169f6ca`
- API Key: stored in `~/.zshrc` as `IMA_OPENAPI_APIKEY`
- If `code=20004` → apikey expired, ask user for fresh key at https://ima.qq.com/agent-interface
- Base URL: `https://ima.qq.com/openapi/note/v1` (not the old `/cgi-bin/agent/chat/` endpoint)

## Python Helper Template

```python
import json, urllib.request, urllib.error

# Load credentials
with open('/home/yxf/.hermes/feishu_todo_creds.json') as f:
    user_token = json.load(f)['user_access_token']
with open('/home/yxf/.hermes/feishu_literature_creds.json') as f:
    base_token = json.load(f)['base_token']

BASE = base_token  # "O26ebCYPRa56Nvsy48icxkMXn6O"

def api(path, method="GET", body=None):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE}{path}"
    headers = {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

## Field IDs Reference

### 文献清单 (tblaWA2qpMhkw2Po)
| 字段名 | Field ID |
|--------|----------|
| 序号 | fldyrNbWCX |
| 文献标题 | fldjL6SW2C |
| 作者 | fld1PxDLoP |
| 年份 | fldbM4yfqS |
| 阶段 | fldIFlCE3D |
| 预计时间（小时） | fldM78MXM1 |
| 重要性 | fldmYSz3GN |
| 状态 | fldAjq1qhy |
| 完成时间 | fldcW2dTs7 |
| 备注 | fldNZXAK4A |

### 阅读进度 (tbl9Teu90g7ADBly)
| 字段名 | Field ID |
|--------|----------|
| 日期 | fldvBJbrhz |
| 文献序号 | fldM1ADt4y |
| 文献标题 | fld19Po0U7 |
| 阅读时长（小时） | fldcmI15Pw |
| 核心发现 | fldu5aWRwF |
| 笔记 | fldizq9iaW |
| 下一步计划 | fldvCNElhw |

### From OpenAlex (tblQOcl30tUp0lmN)
| 字段名 | Field ID |
|--------|----------|
| 文章标题 | fldZyBEmox |
| 引用形式 | fldqhVRzsI |
| 年份 | fldDHJUcIf |
| 期刊/来源 | fldFEXOAzm |
| 关键科学问题（ABC+C2B） | fldnljbGlR |
| 研究类型 | fldCEu4EXs |
| 创新点 | fldKCjERDZ |
| 不足 | fldLf0TRYQ |
| 数据来源 | fldeRHSj7O |
| 方法 | fldwgIwTL3 |
| 主要发现 | fldpKKXXRq |
| 个人备注 | fldCcsnZjh |

## Status Values (文献清单)
- `✅ 已完成`
- `🟡 进行中`
- `⏳ 待开始`

## Importance Values
- `⭐` — 基础
- `⭐⭐` — 重要
- `⭐⭐⭐` — 核心必读

## Workflow
1. 用户说"文献管理"→ 列出文献清单摘要 + 各阶段进度
2. 用户说"找某文献"→ 搜索文献清单 + From OpenAlex
3. 用户说"读完/开始某文献"→ 更新文献清单状态 + 新增阅读进度记录
4. 用户说"添加文献"→ 录入文献清单
5. 用户说"看阅读进度"→ 查询阅读进度表 + 关联文献标题
