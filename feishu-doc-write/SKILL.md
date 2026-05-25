---
name: feishu-doc-write
description: |
  Write content to Feishu (飞书) cloud documents via the docx API.
  Triggers when user says "write to Feishu", "save to Feishu doc", "create Feishu note", etc.
created: 2026-04-22
tags: [飞书, feishu, document-api]
---

# Feishu Doc Write Skill

## Authentication

App ID: `cli_a92714e0d2b8dbc4`
App Secret: `beYfV5HySiekWFYklgipigyGUrXsU7ud`

> ⚠️ For Todo API (task/v2), use user_access_token via OAuth — tenant_access_token does NOT work. See `feishu-todo` skill.

## Core Workflow

### Step 1: Get tenant_access_token

```bash
curl -s -X POST \
  https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a910623283f8dbcb","app_secret":"NrfCFU9KoXNBLx7xbVq2xdr5cIAbsYXL"}'
```

### Step 2: Create document

```bash
curl -s -X POST \
  https://open.feishu.cn/open-apis/docx/v1/documents \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"文档标题"}'
```

Response: `{data: {document: {document_id: "xxx"}}`

### Step 3: Get page block ID

The page block ID = document_id (same value, same ID).

```bash
GET https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks
# page block is items[0], its block_id equals the document_id
```

### Step 4: Insert blocks

**Endpoint**: `POST /open-apis/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children`

Parent block ID = document_id (the page block).

## Block Format Reference

⚠️ CRITICAL DISCOVERY: The Feishu API block format does NOT match official docs in some cases.

| block_type | Content Key | Works? |
|------------|-------------|--------|
| 2 (text) | `"text"` | ✅ YES |
| 2 (text) | `"paragraph"` | ❌ NO (invalid param) |
| 3 (heading1) | `"heading1"` | ✅ YES |
| 4 (heading2) | `"heading2"` | ✅ YES |
| 5 (heading3) | `"heading3"` | ✅ YES |

### Correct paragraph block:

```json
{
  "block_type": 2,
  "text": {
    "elements": [{"text_run": {"content": "Your text here"}}],
    "style": {}
  }
}
```

### Correct heading blocks:

```json
{
  "block_type": 3,
  "heading1": {
    "elements": [{"text_run": {"content": "Heading text"}}],
    "style": {}
  }
}
```

## Batch Insert Pattern (Python)

```python
import subprocess, json, time

def get_token():
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', '{"app_id":"cli_a92714e0d2b8dbc4","app_secret":"beYfV5HySiekWFYklgipigyGUrXsU7ud"}'
    ], capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout)['tenant_access_token']

def insert_blocks(doc_id, token, blocks, batch_idx):
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({"children": blocks, "index": -1})
    ], capture_output=True, text=True, timeout=20)
    data = json.loads(result.stdout)
    n = len(data.get('data', {}).get('children', []))
    print(f"Batch {batch_idx}: code={data.get('code')} blocks={n}")
    return data.get('code') == 0

# Block builders
t  = lambda c: {"block_type": 2,  "text":       {"elements": [{"text_run": {"content": c}}], "style": {}}}
h2 = lambda c: {"block_type": 4,  "heading2":   {"elements": [{"text_run": {"content": c}}], "style": {}}}
h3 = lambda c: {"block_type": 5,  "heading3":   {"elements": [{"text_run": {"content": c}}], "style": {}}}

token = get_token()
doc_id = "YOUR_DOC_ID"

batches = [
    ([h2("标题"), t("内容...")], 1),
    # ... more batches
]
for blocks, idx in batches:
    ok = insert_blocks(doc_id, token, blocks, idx)
    if not ok:
        token = get_token()  # refresh token on failure
        insert_blocks(doc_id, token, blocks, f"{idx}R")
    time.sleep(1)
```

## Insert Rules

- Omit `"index"` field or set to `-1` (append to end)
- Batch max ~20 blocks per request (9 confirmed safe)
- `"children"` not `"blocks"` in request body
- If `code != 0`, refresh token and retry once

## Quick Test (verify auth works)

```bash
# Should return document with title
curl -s https://open.feishu.cn/open-apis/docx/v1/documents/BOXXXY/blocks \
  -H "Authorization: Bearer {token}"
```

## Common Error Codes

- `1770001` "invalid param": Wrong block structure (likely used `paragraph` instead of `text` for block_type 2)
- `99992402`: Wrong parent_block_id

## Document URL Format

`https://feishu.cn/docx/{document_id}`
