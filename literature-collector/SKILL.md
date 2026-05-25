# 文献收集器 | Literature Collector

## 📚 功能描述

学术文献智能收集与管理工具。支持从用户输入中提取文献关键信息，自动存入飞书多维表格，智能识别重复文献并建立关联。

---

## 🎯 触发词

- "文献收藏"、"收藏文献"
- "文献收集"、"收集文献"
- "添加文献"
- "记一篇文献"
- "新建文献"

---

## ✨ 核心功能

### 1. 智能信息提取
从用户输入中提取以下12个字段：
- 文章标题（必填）
- 引用形式（作者+年份）
- 年份
- 期刊/来源
- 关键科学问题（ABC+C2B）
- 研究类型（多选）
- 创新点
- 不足
- 数据来源
- 方法（多选）
- 主要发现
- 个人备注

### 2. 重复检测
- 检测可能重复的文献（基于标题相似度）
- 在个人备注中标注重复文献
- 建立与原文献的关联

### 3. 灵活输入
- 支持结构化输入（字段名: 值）
- 支持自然语言输入（AI提取）
- 缺失信息自动留空，待后续补充

---

## 📊 配置信息

**飞书表格：** 文献笔记
**URL：** https://my.feishu.cn/wiki/BgndwdbhciDZ1Nk9F16cdv59n5e
**app_token：** KHzSbZmu5abRoTs2eMfcmVIcnUf
**table_id：** tblez9UvuXE9PUOX

---

## 🔧 字段映射

| 字段名 | 字段ID | 类型 | 说明 |
|--------|--------|------|------|
| 文章标题 | fld7ZMMEVd | Text | 主键，必填 |
| 引用形式 | fldf7TILct | Text | 作者+年份 |
| 年份 | fldcAIwVxF | Number | 数字格式 |
| 期刊/来源 | fldKy7EhsW | Text | 期刊名/会议名/来源 |
| 关键科学问题（ABC+C2B） | fld1Q1thMY | Text | 科学问题框架 |
| 研究类型 | fldrehkiDk | MultiSelect | 理论/实证/综述等 |
| 创新点 | fldP7fZKc8 | Text | 核心创新贡献 |
| 不足 | fldID1keH3 | Text | 研究局限性 |
| 数据来源 | fld6IWjV3L | Text | 数据集名称/来源 |
| 方法 | fldhiAi9J6 | MultiSelect | 研究方法 |
| 主要发现 | fldXwUNLLt | Text | 核心结论 |
| 个人备注 | fldRA88GQ6 | Text | 阅读笔记/重复标记 |

---

## 💡 使用方式

### 方式1：结构化输入
```
文献收藏：
标题：The Impact of Climate Policy on Economic Growth
作者：Smith & Johnson
年份：2024
期刊：Journal of Environmental Economics
科学问题：气候政策如何影响经济增长？
研究类型：实证研究
方法：面板数据模型、DID方法
发现：气候政策对短期增长有负面影响，但长期促进绿色经济转型
```

### 方式2：自然语言输入
```
收藏一篇文献，Smith和Johnson 2024年发表在环境经济学期刊上的研究，题目是气候政策对经济增长的影响。这是一篇用面板数据和DID方法做的实证研究，发现短期有负面影响但长期促进转型。
```

### 方式3：最小输入
```
添加文献：The Impact of Climate Policy on Economic Growth (2024)
```

---

## 🔄 工作流程

```
用户输入
   ↓
信息提取（AI解析 + literature_collector.py）
   ↓
重复检测（标题相似度匹配，待实现）
   ↓
构建记录数据
   ↓
写入飞书多维表格
   ↓
返回确认信息
```

---

## ⚠️ 当前状态

**已实现：**
- ✅ Skill框架创建完成
- ✅ 文件结构（SKILL.md, config.json, literature_collector.py, README.md）
- ✅ 输入解析（支持结构化和自然语言输入）
- ✅ 字段提取和格式化
- ✅ 字段验证和规范化
- ✅ 飞书字段映射配置
- ✅ 本地测试通过

**待实现：**
- ⏳ 与OpenClaw深度集成（自动触发和写入）
- ⏳ 重复检测功能（标题相似度匹配）
- ⏳ 批量导入功能
- ⏳ 飞书写入权限配置

**已知限制：**
- 飞书写入可能需要额外的权限配置
- 重复检测依赖人工比对（暂未实现自动检测）

---

## ⚙️ 实现细节

### 重复检测算法
```python
# 基于标题相似度的重复检测
def detect_duplicate(title, existing_titles):
    similarity = calculate_similarity(title, existing_titles)
    if similarity > 0.8:  # 相似度阈值
        return existing_titles[max_index]
    return None
```

### 字段填充策略
- **必填字段：** 文章标题（若缺失则提示）
- **可推断字段：** 年份、引用形式（尝试从内容提取）
- **用户输入字段：** 根据用户提供填充
- **留空字段：** 其余字段留空待补

---

## 📝 示例

**用户：** "文献收藏：Smith et al. (2024). Climate Policy and Economic Growth. Journal of Environmental Economics. 研究问题是气候政策对增长的影响，用面板数据做实证，发现短期负面长期正面。"

**输出：**
```
✅ 文献已收藏
📖 标题：Climate Policy and Economic Growth
📝 引用形式：Smith et al. (2024)
📅 年份：2024
📚 期刊：Journal of Environmental Economics
🔬 研究类型：实证研究
🔧 方法：面板数据模型
🎯 主要发现：短期负面影响，长期促进绿色经济转型
📝 记录ID：rec...
```

---

## 🔗 相关技能

- `academic-deep-research` - 学术深度研究
- `feishu-bitable` - 飞书多维表格高级操作
- `notebooklm` - 笔记本AI知识管理

---

*Last Updated: 2026-03-18*
