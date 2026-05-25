# Jupyter + LaTeX PDF报告生成技能

**技能版本**: 1.0
**创建日期**: 2026-03-23
**作者**: AI Assistant
**用途**: 自动化Jupyter Notebook执行、图表生成、PDF转换的完整工作流

---

## 快速开始

### 最简单的方式

```bash
# 1. 进入技能目录
cd /home/yxf/.openclaw/workspace/skills/jupyter-pdf

# 2. 运行技能脚本
./jupyter-pdf.sh generate my_analysis.ipynb
```

就这么简单！脚本会：
1. ✅ 执行notebook中的所有代码
2. ✅ 生成所有图表
3. ✅ 转换为LaTeX
4. ✅ 编译PDF
5. ✅ 显示结果

---

## 功能特性

### 核心功能

- 🚀 **一键生成**: 单个命令完成整个流程
- ⏱️ **超时控制**: 灵活设置执行超时时间
- 📁 **目录管理**: 自定义输出目录
- 📊 **图表统计**: 自动检测并显示生成的图表文件
- ✅ **格式验证**: 验证notebook JSON格式
- 🎨 **彩色输出**: 清晰的终端输出（成功/警告/错误）

### 支持的命令

```bash
# 生成PDF（主命令）
./jupyter-pdf.sh generate notebook.ipynb

# 验证notebook格式
./jupyter-pdf.sh validate notebook.ipynb

# 显示帮助
./jupyter-pdf.sh help
```

### 选项参数

```bash
# 基本使用
./jupyter-pdf.sh generate notebook.ipynb

# 设置超时（默认600秒/10分钟）
./jupyter-pdf.sh generate --timeout 900 notebook.ipynb

# 自定义输出文件名
./jupyter-pdf.sh generate --output my_report.pdf notebook.ipynb

# 设置输出目录
./jupyter-pdf.sh generate --dir ./reports notebook.ipynb

# 组合使用
./jupyter-pdf.sh generate --timeout 1200 --output report.pdf --dir ./output notebook.ipynb
```

---

## 使用场景

### 场景1: 快速原型验证

**场景**: 刚写好notebook，想快速验证是否能正确生成PDF

```bash
# 使用默认设置快速测试
./jupyter-pdf.sh generate my_analysis.ipynb
```

**输出**: 
- ✅ PDF文件: my_analysis.pdf
- ✅ 图表列表
- ✅ 文件大小

### 场景2: 长时间计算

**场景**: 包含复杂计算或大数据处理，需要更长超时

```bash
# 设置15分钟超时
./jupyter-pdf.sh generate --timeout 900 complex_analysis.ipynb
```

**输出**:
- ✅ 足够时间完成计算
- ✅ 自动处理所有步骤

### 场景3: 批量生成多个报告

**场景**: 需要生成多个分析报告

```bash
# 批量生成
./jupyter-pdf.sh generate --output report1.pdf analysis1.ipynb
./jupyter-pdf.sh generate --output report2.pdf analysis2.ipynb
./jupyter-pdf.sh generate --output report3.pdf analysis3.ipynb
```

### 场景4: 组织报告结构

**场景**: 将不同报告输出到特定目录

```bash
# 创建报告目录
mkdir -p ./reports/financial ./reports/technical

# 输出到不同目录
./jupyter-pdf.sh generate --dir ./reports/financial sp500_analysis.ipynb
./jupyter-pdf.sh generate --dir ./reports/technical market_analysis.ipynb
```

---

## Notebook最佳实践

### 推荐结构

```json
{
 "cells": [
   {"cell_type": "markdown", "source": ["# Title"]},
   {"cell_type": "markdown", "source": ["## Summary"]},
   {"cell_type": "code", "source": ["import lib; print('Step 1')"]},
   {"cell_type": "code", "source": ["data = load(); print(data.shape)"]},
   {"cell_type": "code", "source": ["results = analyze(); print(results)"]},
   {"cell_type": "markdown", "source": ["## Chart"]},
   {"cell_type": "code", "source": ["generate_chart(); print('Chart saved')"]},
   {"cell_type": "markdown", "source": ["![图表](chart.png)"]},
   {"cell_type": "markdown", "source": ["## Conclusion"]}
 ]
}
```

### 关键要点

1. **每个步骤都有print输出**
   ```python
   print('Step 1: Loading data...')
   # 代码执行
   print('✅ Step 1 completed')
   ```

2. **不要在markdown中使用.format()**
   ```json
   // ❌ 错误
   {"source": ["Value: {x:.2f}".format(x=5.2)]}
   
   // ✅ 正确
   {"source": ["print(f'Value: {x:.2f}')"]}
   ```

3. **使用合理的超时时间**
   - 简单notebook: 300秒
   - 中等notebook: 600秒
   - 复杂notebook: 900-1200秒

---

## 常见问题

### 问题1: jupyter nbconvert未找到

**错误**: `bash: jupyter: command not found`

**解决方案**:
```bash
pip install jupyter nbconvert
```

### 问题2: xelatex未找到

**警告**: `xelatex未找到，PDF生成可能失败`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex

# macOS
brew install mactex

# 验证安装
which xelatex
```

### 问题3: 超时错误

**错误**: `TimeoutError: Cell execution timed out`

**解决方案**:
```bash
# 增加超时时间
./jupyter-pdf.sh generate --timeout 1200 notebook.ipynb
```

### 问题4: 图片未显示

**错误**: PDF中图片显示为红叉

**解决方案**:
```bash
# 1. 验证图片文件是否生成
ls -lh chart.png

# 2. 确保markdown引用正确
![图表](chart.png)

# 3. 图片路径相对notebook文件
# 不要使用绝对路径
```

### 问题5: JSON格式错误

**错误**: `NotJSONError: Notebook does not appear to be JSON`

**解决方案**:
```bash
# 1. 验证JSON格式
./jupyter-pdf.sh validate notebook.ipynb

# 2. 查看具体错误
python3 -m json.tool notebook.ipynb
```

---

## 完整示例

### 示例1: 金融分析报告

```bash
# 1. 创建notebook
cp template_analysis.ipynb sp500_analysis.ipynb

# 2. 添加代码
# 编辑sp500_analysis.ipynb，添加：
# - yfinance数据获取
# - 技术指标计算
# - mplfinance K线图生成
# - 分析结果输出

# 3. 生成PDF
./jupyter-pdf.sh generate --timeout 900 sp500_analysis.ipynb
```

### 示例2: 学术研究论文

```bash
# 1. 创建notebook
cp template_analysis.ipynb research_paper.ipynb

# 2. 添加代码
# 编辑research_paper.ipynb，添加：
# - 数据收集
# - 统计分析
# - 图表生成（matplotlib）
# - 结论撰写

# 3. 生成PDF
./jupyter-pdf.sh generate --output paper.pdf research_paper.ipynb
```

### 示例3: 数据科学报告

```bash
# 1. 创建notebook
cp template_analysis.ipynb data_science.ipynb

# 2. 添加代码
# 编辑data_science.ipynb，添加：
# - 数据加载
# - 探索性分析（EDA）
# - 特征工程
# - 模型训练
# - 结果可视化

# 3. 生成PDF
./jupyter-pdf.sh generate --timeout 1200 --output ds_report.pdf data_science.ipynb
```

---

## 技能文件说明

### 文件列表

```
skills/jupyter-pdf/
├── README.md                 # 本文件（使用说明）
├── SKILL.md                 # 详细技能文档（最佳实践、错误处理）
└── jupyter-pdf.sh           # 可执行脚本（主程序）
```

### 文件权限

```bash
# 确保脚本可执行
chmod +x jupyter-pdf.sh

# 验证权限
ls -lh jupyter-pdf.sh
# 应该显示: -rwxr-xr-x (包含x)
```

---

## 工作流程图

```
┌─────────────────┐
│  Notebook     │
│  .ipynb     │
└──────┬────────┘
       │
       │ jupyter-pdf.sh generate
       │
       ▼
┌─────────────────┐
│  Execute      │
│  Notebook     │
│  (Code +      │
│   Output)    │
└──────┬────────┘
       │
       │ jupyter nbconvert
       │
       ▼
┌─────────────────┐
│  LaTeX        │
│  .tex         │
└──────┬────────┘
       │
       │ xelatex (3x)
       │
       ▼
┌─────────────────┐
│  PDF          │
│  .pdf         │
└─────────────────┘
```

---

## 技能依赖

### 必需依赖

- **Python**: 3.6+
- **Jupyter Notebook**: >= 1.0
- **nbconvert**: jupyter的nbconvert组件
- **LaTeX**: xelatex（推荐）或pdflatex
- **bash**: 4.0+

### Python包

```bash
pip install jupyter nbconvert pandas numpy matplotlib seaborn

# 金融分析
pip install yfinance mplfinance

# 数据科学
pip install scikit-learn statsmodels
```

---

## 高级用法

### 批量处理

```bash
# 创建批量脚本
#!/bin/bash
for file in *.ipynb; do
    ./jupyter-pdf.sh generate --output "${file%.ipynb}.pdf" "$file"
done
```

### 集成到自动化

```bash
# Cron任务（每天凌晨2点生成报告）
0 2 * * * /path/to/jupyter-pdf.sh generate /path/to/daily_analysis.ipynb

# 监控任务（文件变化时自动生成）
while inotifywait -e modify /path/to/notebook.ipynb; do
    /path/to/jupyter-pdf.sh generate /path/to/notebook.ipynb
done
```

### 自定义模板

```python
# 创建自定义LaTeX模板
# 在notebook中使用
# %%html
# 或
# jupyter nbconvert --to latex --template my_template.tpl
```

---

## 总结

### 核心优势

1. **一键生成**: 单个命令完成整个流程
2. **灵活配置**: 支持超时、输出、目录等选项
3. **错误处理**: 自动检测常见错误并提供建议
4. **可视化输出**: 彩色终端输出，清晰的状态显示
5. **格式验证**: 内置notebook格式验证功能

### 适用场景

- ✅ 金融分析报告
- ✅ 数据科学项目
- ✅ 学术研究论文
- ✅ 业务分析报告
- ✅ 技术文档生成

---

## 获取帮助

```bash
# 显示完整帮助
./jupyter-pdf.sh help

# 验证notebook
./jupyter-pdf.sh validate notebook.ipynb

# 查看技能文档
cat SKILL.md
```

---

**技能版本**: 1.0
**最后更新**: 2026-03-23
**联系方式**: 通过AI Assistant
**适用场景**: 金融分析、数据科学、学术研究、数据报告生成
