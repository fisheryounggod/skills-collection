---
name: office-tools
description: "Handle Word, Excel, PDF, and PowerPoint documents, including reading and text extraction."
---

# Office Tools - 文档处理技能

## 描述
处理Word、Excel、PDF、PowerPoint文档的技能。提供读取、提取文本、简单编辑等功能。

## 环境
- **Python虚拟环境**: `.venv`
- **依赖包**:
  - python-docx - 处理 .docx 文件
  - openpyxl - 处理 .xlsx 文件
  - pypdf2 / pdfplumber - 处理 PDF 文件
  - python-pptx - 处理 .pptx 文件

## 脚本

### scripts/docx-read - 读取Word文档
```bash
./skills/office-tools/scripts/docx-read file.docx
```

提取Word文档的所有文本内容。

### scripts/excel-read - 读取Excel文档
```bash
./skills/office-tools/scripts/excel-read file.xlsx [sheet_name]
```

读取Excel表格内容。可指定工作表名称，否则读取第一个工作表。

### scripts/pdf-read - 读取PDF文档
```bash
./skills/office-tools/scripts/pdf-read file.pdf
```

提取PDF文档的所有文本内容。

### scripts/pptx-read - 读取PowerPoint文档
```bash
./scripts/office-tools/scripts/pptx-read file.pptx
```

提取PowerPoint演示文稿的所有文本内容。

## 使用示例

**Word文档:**
```bash
# 读取文本
./skills/office-tools/scripts/docx-read document.docx

# 统计字数
./skills/office-tools/scripts/docx-read document.docx | wc -w
```

**Excel表格:**
```bash
# 读取整个表格
./skills/office-tools/scripts/excel-read data.xlsx

# 读取指定工作表
./skills/office-tools/scripts/excel-read data.xlsx Sheet2
```

**PDF文档:**
```bash
# 读取文本
./skills/office-tools/scripts/pdf-read report.pdf
```

**PowerPoint:**
```bash
# 读取幻灯片内容
./skills/office-tools/scripts/pptx-read presentation.pptx
```

## 注意事项
- 仅支持较新的文档格式（.docx, .xlsx, .pptx），不支持旧的 .doc, .xls, .ppt 格式
- PDF文本提取依赖于文档中是否包含可选择的文本（扫描的PDF需要OCR）
- 复杂的排版、图片、表格格式化可能无法完美保留
