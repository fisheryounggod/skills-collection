---
name: agnostic-auto
description: |
  诊断系统 - 自动化信息分诊工作流。6步流程：接收→分析→报告→确认→存储→完成。
  支持文字/图片输入，8个分类方向，人工确认后才写入文件系统。
  Use when: user sends content (text/image/screenshot) that needs to be organized, classified, or stored in knowledge base.
homepage: https://github.com/lijigang/ljg-skills
version: "1.0.0"
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "env": ["IMA_OPENAPI_CLIENTID", "IMA_OPENAPI_APIKEY"] },
        "primaryEnv": "IMA_OPENAPI_CLIENTID",
        "optional": ["GOOGLE_API_KEY"]
      },
  }
---

# agnostic-auto

自动化信息分诊系统，让每条有价值输入落到正确位置，避免遗忘在噪音里。

## Setup

```bash
# 必需：IMA笔记API（用于存储分诊结果）
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"

# 可选：Google API（用于图片OCR）
export GOOGLE_API_KEY="your_google_api_key"
```

> 建议将export语句写入~/.bashrc或~/.zshrc

## 核心原则

1. **只分类，不加工**（分诊 ≠ 创作）
2. **保留原文，不丢弃**任何内容
3. **人工确认后才写入**文件系统

## 6步工作流

### Step 1: 接收内容

```bash
# 文字 → 直接分析
# 图片/截图 → OCR提取后分析
```

### Step 2: 分析分类（8个方向，可多选）

**分类列表：**

| 分类ID | 分类名称 | 说明 |
|--------|----------|------|
| 1 | 研究资料 | 学术文献、研究笔记、方法论 |
| 2 | 工具技巧 | 编程技巧、工具使用、工作流优化 |
| 3 | 商业洞察 | 市场分析、商业模式、竞争格局 |
| 4 | 思维认知 | 心理学、哲学、认知科学 |
| 5 | 技术趋势 | 新技术、行业动态、未来预测 |
| 6 | 项目管理 | 任务规划、进度追踪、风险控制 |
| 7 | 学习笔记 | 课程笔记、书籍笔记、概念解释 |
| 8 | 灵感创意 | 产品想法、内容创意、创新点子 |

### Step 3: 输出分诊报告（表格形式）

```markdown
## 📋 分诊报告

### 原始内容
[原始文字或图片描述]

### 分类结果
- [分类1]
- [分类2]

### 建议存储位置
- [目录路径]
- [文件名]
```

### Step 4: 等待用户确认

- ✅ 确认 → 执行存储
- ✏️ 修改 → 按修改后分类执行
- ❌ 跳过 → 结束

### Step 5: 执行存储（按类别路由到对应目录）

**目录结构：**
```
~/openclaw/workspace/
├── research/        # 研究资料
├── tools/           # 工具技巧
├── business/        # 商业洞察
├── thinking/        # 思维认知
├── trends/          # 技术趋势
├── projects/        # 项目管理
├── learning/        # 学习笔记
└── ideas/           # 灵感创意
```

### Step 6: 输出存储完成报告

```markdown
## ✅ 存储完成

### 存储位置
- 文件路径：[完整路径]
- 文件大小：[文件大小]

### 文件信息
- 创建时间：[时间戳]
- 分类标签：[分类列表]

### 下一步
- [建议操作]
```

## API调用示例

### 1. 图片OCR处理

```bash
# 使用Vision API进行OCR
curl -s -X POST "https://vision.googleapis.com/v1/images:annotate" \
  -H "Authorization: Bearer $GOOGLE_API_KEY" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "requests": [
      {
        "image": {
          "source": {
            "imageUri": "[图片URL]"
          }
        },
        "features": [
          {
            "type": "TEXT_DETECTION"
          }
        ]
      }
    ]
  ]
}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
full_text = data['responses'][0]['fullTextAnnotation']['text']
print(full_text)
"
```

### 2. 存储到IMA笔记

```bash
# 新建笔记到指定笔记本
ima_api "import_doc" '{
  "folder_id": "user_list_xxx",
  "content_format": 1,
  "content": "# 标题\n\n正文内容"
}'
```

### 3. 分类辅助函数

```python
# 分类关键词匹配
category_keywords = {
    1: ["研究", "文献", "方法论", "论文", "学术"],
    2: ["工具", "技巧", "工作流", "编程", "效率"],
    3: ["市场", "商业模式", "竞争", "分析", "洞察"],
    4: ["心理", "哲学", "认知", "思维", "心理学"],
    5: ["技术", "趋势", "AI", "区块链", "Web3"],
    6: ["项目", "任务", "进度", "风险", "管理"],
    7: ["学习", "笔记", "书籍", "课程", "概念"],
    8: ["想法", "创意", "产品", "内容", "创新"]
}

def classify_text(text):
    matched_categories = []
    text_lower = text.lower()
    
    for cat_id, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched_categories.append(cat_id)
                break
    
    return matched_categories
```

## 使用示例

### 示例1：处理文字内容

```markdown
用户：这条推文讲的是量化交易的一个新策略，值得深入研究

分诊报告：
原始内容：[推文内容]

分类结果：
- 3. 商业洞察
- 5. 技术趋势

建议存储位置：
- business/量化交易策略-[日期].md
```

### 示例2：处理图片

```markdown
用户：[截图图片]

分诊报告：
原始内容：[OCR提取的文字]

分类结果：
- 2. 工具技巧
- 6. 项目管理

建议存储位置：
- tools/[工具名称]使用技巧-[日期].md
```

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| OCR失败 | 提示用户手动输入文字内容 |
| 分类无匹配 | 默认分类为"灵感创意"，提示用户确认 |
| 存储失败 | 重试3次，失败后告知用户手动保存 |
| API配额不足 | 切换到备用API或本地文件系统 |

## 与其他技能配合

- **ima-note**: 存储分诊结果
- **ljg-word**: 如果内容是英语单词，深度解析
- **content-collector**: 收集外部内容来源

## 注意事项

1. 隐私保护：敏感信息处理时询问用户
2. 分类准确性：建立清晰的分类标准文档
3. 文件命名：遵循统一的命名规范
4. 版本控制：保留原文，不修改原始内容

## 扩展性

### 1. 自定义分类

允许用户添加自定义分类：

```python
# 添加用户自定义分类
custom_categories = {
    9: ["个人日记", "心情", "生活"],
    10: ["财经", "投资", "理财"]
}
```

### 2. 多平台同步

```bash
# 存储到多个平台
# IMA笔记
ima_api "import_doc" "$note_data"

# 飞书文档
feishu_doc_create "$note_data"

# Notion
notion_api "$note_data"
```

### 3. 批量处理

```bash
# 批量分诊历史记录
for file in ~/openclaw/temp/history/*; do
    agnostic_auto_process "$file"
done
```

## 成功指标

- 分诊准确率 > 90%
- 用户确认率 > 80%
- 平均处理时间 < 10秒
- 存储成功率 > 95%
