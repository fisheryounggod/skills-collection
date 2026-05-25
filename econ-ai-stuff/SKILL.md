---
name: econ-ai-stuff
description: Curated collection of AI skills and tools for economists. Resource index for Awesome Econ AI Stuff - includes research workflow, data analysis, academic writing, and economic modeling tools.
---

# Econ AI Stuff - 经济学家AI工具资源索引

本skill是[Awesome Econ AI Stuff](https://github.com/meleantonio/awesome-econ-ai-stuff)的资源索引，帮助你找到和使用适合经济研究的AI工具和技能。

---

## 📚 资源分类

### Research Ideation（研究构思）

1. **research-ideation/search-ideation**
   - 从经济现象生成研究问题
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/research-ideation/

2. **research-ideation/literature-review-assistant**
   - 搜索、总结并综合论文
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/research-ideation/

---

### Literature（文献管理）

3. **literature/latex-econ-model**
   - 在LaTeX中编写经济模型
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/literature/

4. **literature/academic-paper-writer**
   - 基于期刊标准起草论文
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/literature/

---

### Theory（理论构建）

5. **theory/general-equilibrium-model-builder**
   - 构建并求解瓦尔拉斯均衡模型
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/theory/

6. **theory/game-theory-solver**
   - 求解并可视化博弈论问题
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/theory/

---

### Data（数据分析）

7. **data/stata-data-cleaning**
   - Stata数据清理
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/data/

8. **data/api-data-fetcher**
   - 从经济API获取数据（FRED、World Bank）
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/data/

9. **data/python-panel-data**
   - Python面板数据分析
   - GitHub: meleantonio/awesome-econ-ai-stuff/skills/data/

10. **data/stata-regression**
    - Stata回归分析
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/data/

---

### Analysis（分析方法）

11. **analysis/stata-iv-did**
    - Stata中的工具变量分析
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/analysis/

12. **analysis/stata-rdd**
    - 在Stata中运行RDD估计
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/analysis/

13. **analysis/stata-iv-reg**
    - Stata中的IV回归
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/analysis/

14. **analysis/panel-data**
    - 面板数据分析
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/analysis/

---

### Writing（写作工具）

15. **writing/academic-paper-writer**
    - 基于期刊标准起草论文
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/writing/

16. **writing/refereree-response**
    - 起草审稿人报告
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/writing/

17. **writing/latex-tables**
    - 生成出版质量的LaTeX表格
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/writing/

---

### Communication（交流展示）

18. **communication/beamer-presentation**
    - 创建Beamer演示文稿
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/communication/

19. **communication/research-website**
    - 构建学术项目网站
    - GitHub: meleantonio/awesome-econ-ai-stuff/skills/communication/

---

## 🎯 如何使用这些工具

### 在OpenClaw中的使用

这些工具不是标准的OpenClaw技能，而是独立的AI工具。你可以：

1. **克隆仓库**
   ```bash
   cd ~/.openclaw/workspace/skills
   git clone https://github.com/meleantonio/awesome-econ-ai-stuff
   ```

2. **选择需要的技能**
   - 根据你的研究阶段选择合适的工具
   - 阅读每个技能的README文档

3. **配合你的已安装技能使用**
   - **jina-reader** - 读取网页文献
   - **web-search** - 搜索相关资源
   - **filesystem** - 管理数据文件
   - **research-paper-writer** - 写论文（已安装）

### 推荐的工作流

#### 研究流程

```
1. 选题阶段
   ↓
   research-ideation/search-ideation
   ↓
   literature/latex-econ-model
   ↓
2. 文献收集
   ↓
   jina-reader (读取论文）
   ↓
   literature/literature-review-assistant
   ↓
3. 数据分析
   ↓
   data/stata-data-cleaning
   ↓
   data/stata-regression
   ↓
4. 论文写作
   ↓
   writing/academic-paper-writer
   ↓
   communication/beamer-presentation
```

#### 理论模型构建

```
1. 理论建模
   ↓
   theory/general-equilibrium-model-builder
   ↓
   theory/game-theory-solver
   ↓
   literature/latex-econ-model
   ↓
2. 模型求解
   ↓
   theory/general-equilibrium-model-builder
   ↓
   data/stata-iv-did
   ↓
   analysis/stata-regression
   ↓
3. 模型验证
   ↓
   data/stata-rdd
   ↓
   writing/academic-paper-writer
```

---

## 📋 优先级推荐

### 高优先级（核心研究流程）

1. **research-ideation/search-ideation** - 生成研究问题
2. **literature/literature-review-assistant** - 文献综述
3. **literature/latex-econ-model** - 模型构建
4. **writing/academic-paper-writer** - 论文写作

### 中优先级（数据分析）

5. **data/stata-data-cleaning** - 数据准备
6. **analysis/stata-regression** - 回归分析
7. **analysis/stata-iv-did** - 工具变量分析

### 低优先级（辅助工具）

8. **communication/beamer-presentation** - 演示制作
9. **communication/research-website** - 网站构建
10. **theory/game-theory-solver** - 博弈论专用

---

## 🔧 安装指南

### 克隆仓库

```bash
# 克隆到OpenClaw workspace
cd ~/.openclaw/workspace
git clone https://github.com/meleantonio/awesome-econ-ai-stuff

# 或者仅克隆skills目录
git clone --depth 1 --branch main --single-branch \
  https://github.com/meleantonio/awesome-econ-ai-stuff/skills/ \
  econ-ai-skills

# 进入技能目录
cd econ-ai-skills
```

### 手动安装

某些技能可能需要特定的Python包或Stata：

```bash
# 查看requirements.txt
cat path/to/skill/requirements.txt

# 安装依赖
pip install -r path/to/skill/requirements.txt
```

### 配置环境

某些工具可能需要：

1. **Stata** - 确保Stata在PATH中
2. **LaTeX** - 安装完整的LaTeX发行版
3. **Python** - 某些工具需要特定的Python包
4. **R** - 某些工具可能需要R

---

## 📚 与你现有OpenClaw技能的整合

### 已安装的相关技能

你现在有这些相关技能可以配合使用：

1. **research-paper-writer** - 研究论文写作
2. **jina-reader** - 网页文献读取
3. **web-search** - 搜索学术资源
4. **filesystem** - 管理研究文件
5. **hk-ai-stock-expert** - 港股投研（可以与经济分析结合）

### 推荐的组合使用

```
研究工作流：
┌─────────────────────────────────────┐
│  1. 文献搜索                         │
│     ├── web-search                  │
│     └── jina-reader               │
│                                      │
│  2. 文献综述                          │
│     ├── awesome-econ-ai-stuff      │
│     │   └── literature-review       │
│     ├── notebooklm-skill            │
│     └── summarize                │
│                                      │
│  3. 模型构建                          │
│     ├── awesome-econ-ai-stuff      │
│     │   └── latex-econ-model         │
│     └── research-paper-writer       │
│                                      │
│  4. 数据分析                          │
│     ├── awesome-econ-ai-stuff      │
│     │   └── stata-regression       │
│     ├── yahoo-finance-cli          │
│     └── exchange-rates            │
│                                      │
│  5. 论文写作                          │
│     ├── awesome-econ-ai-stuff      │
│     │   ├── academic-paper-writer  │
│     │   └── latex-tables          │
│     └── research-paper-writer       │
│                                      │
│  6. 展示与发布                       │
│     ├── awesome-econ-ai-stuff      │
│     │   └── beamer-presentation    │
│     └── filesystem                │
└─────────────────────────────────────┘
```

---

## 💡 使用建议

### 1. 从简单开始

- 先使用**research-ideation**生成研究问题
- 用**jina-reader**读取几篇论文测试
- 使用**literature-review-assistant**做文献综述

### 2. 逐步增加复杂度

- 熟悉后再使用**data/stata-regression**做回归
- 掌握LaTeX后再用**latex-econ-model**写模型
- 文献框架清晰后再用**academic-paper-writer**写作

### 3. 定期更新

- awesome-econ-ai-stuff是一个活跃维护的仓库
- 定期检查更新和新功能
- 关注项目的GitHub Discussions

---

## 🔗 相关资源

- **主仓库：** https://github.com/meleantonio/awesome-econ-ai-stuff
- **文档：** 仓库中的每个skill都有详细的README
- **问题反馈：** GitHub Issues
- **贡献指南：** CONTRIBUTING.md

---

## 🎓 经济研究AI工具生态系统

这个资源集合提供了从研究构思到论文发表的全流程支持：

```
研究构思 → 文献搜索 → 文献综述 → 模型构建 → 数据分析 → 论文写作 → 展示发表
   ↓          ↓          ↓          ↓          ↓          ↓          ↓
问题生成    论文获取    论文综合    数学模型    数据处理    草稿    演示文稿
```

结合你的OpenClaw已安装技能，你现在拥有了一个完整的AI辅助经济研究工作流。
