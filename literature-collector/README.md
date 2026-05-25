# 文献收集器使用指南

## 📦 安装位置

```
~/.openclaw/workspace/skills/literature-collector/
```

---

## 🚀 快速开始

### 触发方式

在聊天中使用以下任一触发词：
- "文献收藏"
- "收藏文献"
- "文献收集"
- "收集文献"
- "添加文献"
- "记一篇文献"
- "新建文献"

---

## 📝 输入格式示例

### 方式1：结构化输入（推荐）

```
文献收藏：
标题：The Impact of Climate Policy on Economic Growth
作者：Smith & Johnson
年份：2024
期刊：Journal of Environmental Economics
科学问题：气候政策如何影响经济增长？
研究类型：实证研究, 政策研究
创新点：首次使用跨国面板数据分析气候政策的长期效应
不足：数据仅覆盖OECD国家
数据来源：OECD数据库, World Bank
方法：面板数据模型, DID方法
主要发现：气候政策对短期增长有负面影响，但长期促进绿色经济转型
备注：重点关注政策传导机制
```

### 方式2：自然语言输入

```
收藏一篇文献，Smith和Johnson 2024年发表在环境经济学期刊上的研究，题目是"The Impact of Climate Policy on Economic Growth"。这是一篇用面板数据和DID方法做的实证研究和政策研究，发现短期有负面影响但长期促进绿色经济转型。
```

### 方式3：最小输入

```
添加文献：The Impact of Climate Policy on Economic Growth (2024)
```

---

## 🔧 技术实现

### 文件结构

```
literature-collector/
├── SKILL.md                 # 技能说明文件（OpenClaw读取）
├── config.json             # 配置文件（字段映射、设置）
├── literature_collector.py  # 核心实现脚本
└── README.md               # 使用说明（本文件）
```

### 配置说明

**config.json** 包含：
- `bitable`: 飞书表格信息（app_token, table_id, URL）
- `fields`: 12个字段的详细配置（ID、名称、类型、是否必填）
- `settings`: 设置项（相似度阈值、自动检测重复等）

### 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| 文章标题 | Text | ✅ | 主键，用于识别文献 |
| 引用形式 | Text | ❌ | 格式：作者 (年份) |
| 年份 | Number | ❌ | 4位数字 |
| 期刊/来源 | Text | ❌ | 期刊名、会议名等 |
| 关键科学问题（ABC+C2B） | Text | ❌ | 研究的核心问题 |
| 研究类型 | MultiSelect | ❌ | 理论/实证/综述等 |
| 创新点 | Text | ❌ | 研究的核心贡献 |
| 不足 | Text | ❌ | 研究的局限性 |
| 数据来源 | Text | ❌ | 数据集名称或来源 |
| 方法 | MultiSelect | ❌ | 具体研究方法 |
| 主要发现 | Text | ❌ | 核心结论 |
| 个人备注 | Text | ❌ | 阅读笔记或重复标记 |

---

## 🧪 测试脚本

### 本地测试

```bash
cd ~/.openclaw/workspace/skills/literature-collector
python3 literature_collector.py "文献收藏：标题：测试文献；年份：2024"
```

### 测试输出示例

```
解析结果：{
  "title": "测试文献",
  "year": 2024
}

飞书格式：{
  "fld7ZMMEVd": "测试文献",
  "fldcAIwVxF": 2024
}

📖 标题：测试文献
📅 年份：2024
```

---

## 🔗 与OpenClaw集成

### 在OpenClaw中使用

1. **触发技能**：用户发送包含触发词的消息
2. **解析输入**：literature_collector.py 提取字段信息
3. **检测重复**：（待实现）检查是否有相似标题的文献
4. **写入飞书**：调用 `feishu_bitable_create_record` 工具
5. **返回确认**：显示收藏成功的摘要信息

### 重复检测逻辑（待实现）

```python
# 伪代码
existing_records = feishu_bitable_list_records(...)
existing_titles = [record['title'] for record in existing_records]

if calculate_similarity(new_title, existing_titles) > 0.8:
    # 在个人备注中标记重复
    fields['notes'] = f"⚠️ 可能重复：与 {duplicate_title} 相似"
```

---

## 🎯 高级功能

### 1. 批量导入

```
收藏多篇文献：
1. 文献A：标题...；年份：2024
2. 文献B：标题...；年份：2023
3. 文献C：标题...；年份：2022
```

### 2. 自动补充

对于已存在的文献，可以后续补充信息：
```
补充文献记录[record_id]：
创新点：...
不足：...
```

### 3. 检索和导出

（待实现）
- 按关键词检索文献
- 导出为BibTeX格式
- 生成文献综述框架

---

## ⚙️ 自定义配置

### 修改默认表格

编辑 `config.json`：
```json
{
  "bitable": {
    "app_token": "你的app_token",
    "table_id": "你的table_id",
    "url": "你的表格URL"
  }
}
```

### 添加自定义字段

1. 在飞书表格中创建新字段
2. 在 `config.json` 中添加字段配置
3. 更新 `literature_collector.py` 中的解析逻辑

---

## 🐛 常见问题

### Q: 解析错误，标题未提取到？
A: 检查输入格式，确保使用"标题："或"Title:"标记

### Q: 多选字段选项不匹配？
A: 检查 `config.json` 中的选项列表，确保与飞书表格一致

### Q: 如何查看飞书表格的字段ID？
A: 使用 `feishu_bitable_list_fields` 工具查询

---

## 📚 相关资源

- [飞书多维表格API文档](https://open.feishu.cn/document/server-docs/docs/bitable-v1)
- [OpenClaw技能开发指南](https://docs.openclaw.ai/skills)
- [学术研究助手相关技能](~/.openclaw/workspace/skills/academic-deep-research/)

---

## 🔄 更新日志

**2026-03-18**
- ✅ 创建基础框架
- ✅ 实现12个字段的配置
- ✅ 实现输入解析和格式化
- ✅ 添加使用文档
- ⏳ 待实现：重复检测功能
- ⏳ 待实现：批量导入功能

---

*Last Updated: 2026-03-18*
