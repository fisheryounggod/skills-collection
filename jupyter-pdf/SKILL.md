---
title: "Jupyter + LaTeX PDF报告生成技能"
description: "自动化Jupyter Notebook执行、图表生成、PDF转换的完整工作流。适用于金融分析、数据科学、学术研究等需要生成专业PDF报告的场景。"
category: automation
priority: 🔴
last_verified: 2026-03-23
tags: [jupyter, latex, pdf, automation, report, nbconvert, yfinance]
---

# Jupyter + LaTeX PDF报告生成技能

**技能用途**: 自动化Jupyter Notebook执行、图表生成、PDF转换的完整工作流
**适用场景**: 金融分析、数据科学、学术研究、数据报告生成

---

## 快速开始

### 最简单的方式
```bash
# 使用本技能生成PDF报告
jupyter-pdf generate my_analysis.ipynb
```

### 完整选项
```bash
# 带超时设置
jupyter-pdf generate --timeout 600 my_analysis.ipynb

# 自定义输出文件名
jupyter-pdf generate --output report.pdf my_analysis.ipynb

# 查看帮助
jupyter-pdf --help
```

---

## 工作流程

### 第1步：执行Jupyter Notebook

**目的**: 运行notebook中的所有代码，生成输出结果

```python
# 自动执行以下步骤
1. 数据获取（yfinance/API/文件）
2. 数据处理（清洗、转换、计算）
3. 图表生成（matplotlib/seaborn/mplfinance）
4. 分析计算（统计、技术指标）
5. 保存图表文件（.png/.jpg）
```

**关键点**:
- ✅ 使用`--execute`标志确保代码运行
- ✅ 设置合理的超时时间（数据下载需要时间）
- ✅ 每个步骤都有print输出，便于调试

### 第2步：转换为LaTeX

**目的**: 将notebook转换为LaTeX源码，用于PDF生成

```bash
# nbconvert自动执行
jupyter nbconvert --to latex notebook.ipynb
```

**生成内容**:
- `notebook.tex` - LaTeX源码文件
- 包含所有markdown单元格（转换为LaTeX格式）
- 包含代码单元格（使用verbatim环境）
- 包含输出结果

### 第3步：编译PDF

**目的**: 使用xelatex编译LaTeX源码，生成最终PDF

```bash
# nbconvert自动调用
xelatex notebook.tex -quiet  # 第1次编译
xelatex notebook.tex -quiet  # 第2次编译（处理交叉引用）
xelatex notebook.tex -quiet  # 第3次编译（最终生成）
```

**为什么需要3次？**
- 第1次: 生成辅助文件（.aux等）
- 第2次: 处理交叉引用（label/ref）
- 第3次: 确保所有引用正确

---

## 关键最佳实践

### 1. Notebook结构设计

#### ✅ 推荐结构
```json
{
 "cells": [
   {"cell_type": "markdown", "source": ["# 标题"]},
   {"cell_type": "markdown", "source": ["## Executive Summary"]},
   {"cell_type": "code", "source": ["import library; print('Step 1')"]},
   {"cell_type": "code", "source": ["data = load(); print(data.shape)"]},
   {"cell_type": "markdown", "source": ["## Analysis"]},
   {"cell_type": "code", "source": ["results = analyze(); print(results)"]},
   {"cell_type": "markdown", "source": ["![图表](chart.png)"]},
   {"cell_type": "markdown", "source": ["## Conclusion"]}
 ]
}
```

#### ❌ 避免的结构
```json
{
 "cells": [
   {"cell_type": "code", "source": ["# 没有print，不知道执行到哪里"]},
   {"cell_type": "markdown", "source": ["Value: {x:.2f}".format(x=5.2)]}
 ]
}
```

### 2. 数据获取最佳实践

#### yfinance数据（金融数据）
```python
import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# ✅ 完整的数据获取流程
print('Step 1: Downloading data...')
data = yf.download('^GSPC', start='2026-01-01', end=today)
print(f'Data shape: {data.shape}')

# ✅ 处理MultiIndex
if isinstance(data.columns, pd.MultiIndex):
    print('Detected MultiIndex, processing...')
    level0 = data.columns.get_level_values(0).tolist()
    data_simple = data.copy()
    data_simple.columns = level0  # 关键：不要用droplevel(0)
    data_indexed = data_simple
else:
    data_indexed = data

print(f'Columns: {data_indexed.columns.tolist()}')
print('✅ Step 1 completed')
```

**关键点**:
- 使用`get_level_values(0)`而非`droplevel(0)`
- 不要在markdown单元格中使用`.format()`
- 每个步骤都有明确的print输出

### 3. 技术指标计算最佳实践

#### RSI计算（避免除零）
```python
# ✅ 健壮的RSI计算
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()

# 关键：处理除零
loss = loss.replace(0, np.nan)
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

# 处理可能的inf/nan
data['RSI'] = data['RSI'].fillna(50.0)
print('RSI calculation completed')
```

#### 移动平均线（避免NaN）
```python
# ✅ 使用min_periods参数
data['MA20'] = data['Close'].rolling(window=20, min_periods=1).mean()
data['MA60'] = data['Close'].rolling(window=60, min_periods=1).mean()
```

### 4. 图表生成最佳实践

#### matplotlib/seaborn
```python
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ 完整的图表生成流程
fig, axes = plt.subplots(figsize=(12, 8))

# 绘图
axes.plot(data.index, data['Close'], label='Price')
axes.plot(data.index, data['MA20'], label='MA20')
axes.legend()

# 保存图片
chart_file = 'chart.png'
fig.savefig(chart_file, dpi=300, bbox_inches='tight')
print(f'Chart saved: {chart_file}')
plt.close(fig)
```

#### mplfinance（K线图）
```python
import mplfinance as mpf

# ✅ 完整的K线图生成流程
mpf_style = mpf.make_mpf_style(base_mpf_style='yahoo', y_on_right=False)

add_plot = [
    mpf.make_addplot(data['MA20'], color='orange', width=1.2),
    mpf.make_addplot(data['MA60'], color='purple', width=1.2),
    mpf.make_addplot(data['RSI'], panel=1, color='blue'),
]

fig, axes = mpf.plot(
    data,
    type='candle',
    style=mpf_style,
    title='Title',
    volume=True,
    addplot=add_plot,
    panel_ratios=(3, 1),
    figsize=(16, 10),
    returnfig=True
)

chart_file = 'kline_chart.png'
fig.savefig(chart_file, dpi=300, bbox_inches='tight')
print(f'K-line chart saved: {chart_file}')
```

### 5. nbconvert最佳实践

#### 执行并转换
```bash
# ✅ 带超时的完整执行
jupyter nbconvert --execute --to pdf \
    --ExecutePreprocessor.timeout=600 \
    notebook.ipynb
```

#### 超时设置建议
- **简单notebook**（只有计算）: 300秒（5分钟）
- **中等notebook**（包含数据下载）: 600秒（10分钟）
- **复杂notebook**（包含图表生成）: 900秒（15分钟）
- **非常复杂**: 1200秒（20分钟）

---

## 常见错误与解决方案

### 错误1: KeyError: 'Close'

**症状**:
```
KeyError: 'Close'
File "/pandas/core/frame.py", line 4378, in DataFrame.__getitem__
```

**根本原因**: yfinance返回MultiIndex结构

**解决方案**:
```python
if isinstance(data.columns, pd.MultiIndex):
    level0 = data.columns.get_level_values(0).tolist()
    data_simple = data.copy()
    data_simple.columns = level0  # 关键
    data_indexed = data_simple
```

### 错误2: ValueError: zero-size array

**症状**:
```
ValueError: zero-size array to reduction operation maximum
File "/numpy/lib/_nanfunctions_impl.py", line 492, in nanmax
```

**根本原因**: RSI计算中除零

**解决方案**:
```python
loss = loss.replace(0, np.nan)
rs = gain / loss
```

### 错误3: NotJSONError: Notebook does not appear to be JSON

**症状**:
```
nbformat.reader.NotJSONError: Notebook does not appear to be JSON
Expecting ',' delimiter: line 310 column 36
```

**根本原因**: markdown单元格中使用了Python格式化字符串

**解决方案**:
```json
// ❌ 错误
{
  "cell_type": "markdown",
  "source": ["Value: {x:.2f}%".format(x=5.2)]
}

// ✅ 正确
{
  "cell_type": "code",
  "source": ["print(f'Value: {x:.2f}%')"]
}
```

### 错误4: TimeoutError: Cell execution timed out

**症状**:
```
TimeoutError: Cell execution timed out
```

**根本原因**: 数据下载或图表生成时间过长

**解决方案**:
```bash
jupyter nbconvert --execute --to pdf \
    --ExecutePreprocessor.timeout=1200 \
    notebook.ipynb
```

### 错误5: 图片未显示

**症状**: PDF中图片显示为红叉或空白

**根本原因**:
- 图片文件路径错误
- 图片文件未生成
- 文件名不匹配

**解决方案**:
```bash
# 1. 检查图片文件
ls -lh chart.png

# 2. 确保notebook中的引用正确
# markdown中：![图表](chart.png)

# 3. 图片路径相对notebook文件
# 不要使用绝对路径
```

---

## 技能模板

### 完整的notebook模板

**文件名**: `template_analysis.ipynb`

```json
{
 "cells": [
   {
     "cell_type": "markdown",
     "metadata": {},
     "source": ["# Analysis Report\n\n**Date**: {date}\n**Tool**: Jupyter + LaTeX"]
   },
   {
     "cell_type": "markdown",
     "metadata": {},
     "source": ["## Executive Summary\n\nBrief overview of the analysis..."]
   },
   {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
        "import pandas as pd\n",
        "import matplotlib.pyplot as plt\n",
        "from datetime import datetime\n",
        "\n",
        "print('Step 1: Loading data...')"
     ]
   },
   {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
        "# 数据获取代码\n",
        "data = load_data()\n",
        "print(f'Data shape: {data.shape}')\n",
        "print('✅ Step 1 completed')"
     ]
   },
   {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
        "# 数据分析代码\n",
        "results = analyze_data(data)\n",
        "print(results)\n",
        "print('✅ Step 2 completed')"
     ]
   },
   {
     "cell_type": "markdown",
     "metadata": {},
     "source": ["## Chart"]
   },
   {
     "cell_type": "code",
     "execution_count": null,
     "metadata": {},
     "outputs": [],
     "source": [
        "# 图表生成代码\n",
        "generate_chart(data)\n",
        "print('✅ Step 3 completed')"
     ]
   },
   {
     "cell_type": "markdown",
     "metadata": {},
     "source": ["![图表](chart.png)\n\nChart description..."]
   },
   {
     "cell_type": "markdown",
     "metadata": {},
     "source": ["## Conclusion\n\nSummary of findings..."]
   }
 ],
 "metadata": {
   "kernelspec": {
     "display_name": "Python 3",
     "language": "python",
     "name": "python3"
   },
   "language_info": {
     "name": "python",
     "codemirror_mode": {"name": "ipython", "version": 3},
     "file_extension": ".py",
     "mimetype": "text/x-python",
     "nbconvert_exporter": "python",
     "pygments_lexer": "ipython3",
     "version": "3.8.0"
   }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
```

### 一键生成脚本模板

**文件名**: `generate_pdf.sh`

```bash
#!/bin/bash
# Jupyter + LaTeX -> PDF 一键生成脚本

set -e

NOTEBOOK_FILE=${1:-"template_analysis.ipynb"}
PDF_FILE=${2:-"report.pdf"}
TIMEOUT=${3:-600}

echo "=========================================="
echo "  Jupyter + LaTeX -> PDF Generator"
echo "=========================================="
echo ""
echo "Notebook: $NOTEBOOK_FILE"
echo "PDF: $PDF_FILE"
echo "Timeout: ${TIMEOUT}s"
echo ""

# 执行并转换
echo "📋 Executing notebook..."
jupyter nbconvert --execute --to pdf \
    --ExecutePreprocessor.timeout=$TIMEOUT \
    "$NOTEBOOK_FILE"

# 检查结果
if [ -f "$PDF_FILE" ]; then
    SIZE=$(ls -lh "$PDF_FILE" | awk '{print $5}')
    echo ""
    echo "=========================================="
    echo "  ✅ PDF generated successfully!"
    echo "=========================================="
    echo ""
    echo "📦 File: $PDF_FILE ($SIZE)"
    echo ""
    
    # 询问是否打开
    read -p "Open PDF now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "$PDF_FILE" 2>/dev/null || \
        open "$PDF_FILE" 2>/dev/null || \
        echo "Cannot auto-open, please open manually"
    fi
else
    echo ""
    echo "❌ Error: PDF generation failed"
    echo "Please check notebook for errors"
    exit 1
fi

echo ""
echo "✅ Completed!"
```

---

## 使用示例

### 示例1: 金融数据分析报告

```bash
# 1. 创建notebook（使用模板）
cp template_analysis.ipynb sp500_analysis.ipynb

# 2. 编辑notebook，添加你的代码
# 数据获取、分析、图表生成

# 3. 生成PDF
./generate_pdf.sh sp500_analysis.ipynb sp500_report.pdf 600
```

### 示例2: 学术研究论文

```bash
# 1. 使用nbconvert模板
jupyter nbconvert --to latex --template classic my_paper.ipynb

# 2. 编译LaTeX（使用学术模板）
pdflatex my_paper.tex

# 3. 生成PDF
# PDF将自动生成
```

### 示例3: 数据科学报告

```bash
# 1. 使用技能生成
jupyter-pdf generate --timeout 900 data_analysis.ipynb

# 2. 查看结果
# PDF将自动生成在当前目录
```

---

## 故障排查

### 问题1: nbconvert未安装

**症状**:
```
bash: jupyter: command not found
```

**解决方案**:
```bash
pip install jupyter nbconvert
```

### 问题2: LaTeX未安装

**症状**:
```
bash: xelatex: command not found
```

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex

# macOS
brew install mactex

# 检查安装
which xelatex
xelatex --version
```

### 问题3: 依赖包缺失

**症状**:
```
ModuleNotFoundError: No module named 'yfinance'
```

**解决方案**:
```bash
pip install yfinance mplfinance pandas numpy matplotlib seaborn
```

---

## 性能优化

### 1. 减少执行时间

```python
# ❌ 慢：逐行处理
for i in range(len(data)):
    result[i] = complex_calculation(data.iloc[i])

# ✅ 快：向量化操作
result = data.apply(lambda x: complex_calculation(x))
# 或更快：使用pandas内置
result = data['col'].rolling(window=20).mean()
```

### 2. 减少PDF生成时间

```bash
# ❌ 慢：不必要的完整执行
jupyter nbconvert --execute --to pdf notebook.ipynb

# ✅ 快：先执行后转换
jupyter nbconvert --execute notebook.ipynb
jupyter nbconvert --to pdf notebook.ipynb
```

---

## 总结

### 关键要点

1. **Notebook设计**
   - 每个步骤都有明确的print输出
   - markdown单元格不包含`.format()`
   - 代码单元格execution_count初始为null

2. **数据处理**
   - yfinance的MultiIndex使用`get_level_values(0)`
   - RSI计算使用`replace(0, np.nan)`
   - rolling计算使用`min_periods=1`

3. **图表生成**
   - 保存图片使用相对路径
   - 文件名与markdown引用一致
   - 使用合理的dpi和figsize

4. **PDF生成**
   - 使用`--execute`确保代码执行
   - 设置合理的超时时间
   - 理解xelatex需要编译3次

5. **错误处理**
   - 验证notebook JSON格式
   - 添加print输出便于调试
   - 使用try-catch处理关键操作

### 快速参考

| 任务 | 命令 |
|------|--------|
| **执行notebook** | `jupyter nbconvert --execute notebook.ipynb` |
| **转PDF（已执行）** | `jupyter nbconvert --to pdf notebook.ipynb` |
| **完整生成** | `jupyter nbconvert --execute --to pdf --ExecutePreprocessor.timeout=600 notebook.ipynb` |
| **验证JSON** | `python3 -m json.tool notebook.ipynb` |

---

**技能版本**: 1.0
**最后更新**: 2026-03-23
**作者**: AI Assistant
**适用场景**: 金融分析、数据科学、学术研究
