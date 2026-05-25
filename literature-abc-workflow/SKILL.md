---
name: literature-abc-workflow
description: |
  文献ABC-C2B分析工作流：从 IMA 笔记 → 结构化 ABC-C2B 分析 → 导入飞书 Base 文献表。
  触发词：「分析文献」「做ABC」「C2B分析」「导入文献」「文献pipeline」「文献管理流程」「ABC文献」
  核心场景：读论文 → IMA笔记+ABC框架 → 飞书文献表自动填充
created: 2026-04-23
tags: [文献管理, ABC分析, C2B, IMA, 飞书, feishu, literature, research workflow]
---

# ABC-C2B 文献分析工作流

> ⚠️ **安全注意**：所有 API keys/tokens 禁止内联写入 SKILL.md，会被安全扫描拦截并拒绝。
> 必须存入 `~/.hermes/*.json` 文件，技能代码通过读取文件获取凭证。

将论文阅读笔记转化为结构化知识，导入飞书 Base 文献管理系统的标准化流程。

## 凭证文件

- **IMA**: `~/.hermes/ima_creds.json` → `client_id`, `api_key`
- **飞书**: `~/.hermes/feishu_todo_creds.json` → `user_access_token`
- **飞书Base**: `~/.hermes/feishu_literature_creds.json` → `base_token`

## 核心概念

### ABC Framework（主体-行为-约束）
- **A = Agents（主体）**：模型/研究中的决策者是谁？（如：新兴市场央行、全球机构投资者、代表性家庭）
- **B = Behavior（行为）**：主体的行为是什么？（如：跨境资本配置、资产组合调整、货币政策决策）
- **C = Constraint（约束）**：什么约束限制行为？（如：资本管制、汇率制度、信息不对称、预算约束）

### C2B（Back-to-Core，关键科学问题）
从具体研究问题提炼：**这篇论文解决的最核心科学问题是什么？** 为什么这个问题重要？

---

## Pipeline 总览

```
论文/文档  →  IMA笔记(ABC-C2B模板)  →  飞书Base文献表
                        ↓
              主体/行为/约束/B2C/流派/贡献/不足/方法/发现
```

---

## Step 1：IMA 笔记操作

### API Helper（Python）
```python
import json, urllib.request, os

with open('/home/yxf/.hermes/ima_creds.json') as f:
    creds = json.load(f)
CLIENTID = creds['client_id']
APIKEY = creds['api_key']

BASE_URL = "https://ima.qq.com/openapi/note/v1"

def ima_api(endpoint, body):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/{endpoint}",
        data=data,
        headers={
            "ima-openapi-clientid": CLIENTID,
            "ima-openapi-apikey": APIKEY,
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

### 搜索已有笔记
```python
r = ima_api("search_note_book", {
    "search_type": 0,  # 0=标题搜索, 1=正文搜索
    "query_info": {"title": "论文标题关键词"},
    "start": 0, "end": 10
})
# 返回: r['docs'][i]['doc']['basic_info']['docid']
```

### 读取笔记正文
```python
r = ima_api("get_doc_content", {
    "doc_id": "DOCID",
    "target_content_format": 0  # 0=纯文本
})
content = r['data']['content']
```

### 创建新笔记（ABC-C2B分析结果）
```python
NOTE_CONTENT = f"""# {{标题}}

## 文献信息
- **作者**: {{作者}}
- **年份**: {{年份}}
- **期刊**: {{期刊}}

## ABC Framework
### A - 主体（Agents）
{{模型中的决策主体：央行、家庭、企业、政府、投资者等}}
### B - 行为（Behavior）
{{主体采取的具体行动和经济行为}}
### C - 约束（Constraint）
{{限制行为的关键约束条件}}

## C2B - 关键科学问题
{{这篇论文解决的最核心科学问题是什么？为什么重要？}}

## 研究贡献
- **主要贡献**: {{论文的核心创新和贡献}}
- **引用目的**: {{为什么引用这篇论文——用于哪个子研究问题}}

## 研究局限
- **不足**: {{数据/方法/样本/理论等方面的局限性}}

## 方法与数据
- **实证方法**: {{使用的计量/理论方法}}
- **数据来源**: {{数据类型和来源}}

## 核心发现
{{最重要的实证/理论结果}}

## 流派分类
{{理论归属：如 全球金融周期 / 资本流动波动性 / CBDC / DSGE等}}

## 重要性
{{⭐/⭐⭐/⭐⭐⭐}}
"""

r = ima_api("import_doc", {
    "content_format": 1,
    "content": NOTE_CONTENT,
    "folder_id": "folder729160ed3f4dd20e"  # 研究笔记 folder
})
# ⚠️ 关键发现：import_doc 返回的是 note_id，不是 doc_id！
# 完整返回示例: {"code": 0, "data": {"note_id": "7452925144103204"}}
# 如果需要后续读取/导入飞书，需用 note_id 查询
note_id = r['data']['note_id']
```

### 重要文件夹 ID
- `folder729160ed3f4dd20e` — 研究笔记
- `folderbedca736dec7a63b` — CBDC
- `folder6ec6e72e3aad0324` — 自我认知
- `folderc755ffe356d9f396` — archived

---

## Step 2：飞书 Base 写入

### API Helper（Python）
```python
import json, urllib.request

with open('/home/yxf/.hermes/feishu_todo_creds.json') as f:
    user_token = json.load(f)['user_access_token']
with open('/home/yxf/.hermes/feishu_literature_creds.json') as f:
    base_token = json.load(f)['base_token']

BASE = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_token}"

def fs_api(path, method="GET", body=None):
    url = BASE + path
    headers = {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

### ⚠️ 关键规则：写入用字段名，不用 field_id
飞书 Bitable 写入记录时，**`fields` 字典的 key 必须是字段中文名**。

### Base 表格一览
| 表名 | Table ID | 用途 |
|------|-----------|------|
| CBDC文献 | `tblc549ns2xQOtBI` | CBDC领域 ABC-C2B 结构化文献 |
| 资本流动实证分析 | `tblSugmyUAXTcmPd` | 资本流动实证文献 ABC-C2B 模板 |

### 字段对照（ABC-C2B类表格通用）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 编号 | Number | 整数，非字符串 |
| 文献 | Text | 引用格式 |
| 标题 | Text | 英文标题 |
| 年份 | Number | 整数，如 `2024` |
| 期刊 | Text | 期刊/Working Paper |
| 主体（Agents） | Text | ABC框架 |
| 行为（Behavior） | Text | ABC框架 |
| 约束（Constraint） | Text | ABC框架 |
| 关键科学问题（B2C） | Text | 核心研究问题 |
| 流派分类 | Text | 理论流派 |
| 主要贡献及引用目的 | Text | 贡献+引用理由 |
| 不足 | Text | 研究局限 |
| 研究数据 | Text | 数据来源 |
| 实证方法 | Text | 计量方法 |
| 主要发现 | Text | 核心发现 |
| 重要性 | Text | ⭐/⭐⭐/⭐⭐⭐ |

### 写入记录
```python
record = {
    "fields": {
        "编号": 7,
        "文献": "Author, 2024",
        "标题": "Paper Title",
        "年份": 2024,  # 必须整数
        "期刊": "Journal Name",
        "主体（Agents）": "...",
        "行为（Behavior）": "...",
        "约束（Constraint）": "...",
        "关键科学问题（B2C）": "...",
        "流派分类": "...",
        "主要贡献及引用目的": "...",
        "不足": "...",
        "研究数据": "...",
        "实证方法": "...",
        "主要发现": "...",
        "重要性": "⭐⭐"
    }
}
r = fs_api(f"/tables/{TABLE_ID}/records", method="POST", body=record)
# code=0 = 成功
```

---

## 完整工作流

```
1. 用户提供：论文名称 或 IMA 笔记标题
2. 搜索 IMA 笔记 → 获取 doc_id
3. 读取笔记正文 → 解析 ABC-C2B 结构
4. 在 IMA 创建/更新结构化 ABC-C2B 笔记
5. 解析后写入飞书目标表
6. 返回导入结果
```

---

## 常见问题排查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `FieldNameNotFound` | 写入时用了 field_id 而非字段名 | 用中文字段名 |
| `NumberFieldConvFail` | Number型字段传了字符串 | 年份传 `2024` 而非 `"2024"` |
| `code=20004` | IMA apikey 过期 | 到 https://ima.qq.com/agent-interface 刷新 |
| `code=1254045` | 飞书 token 过期 | 重新 OAuth 授权 |
