---
name: econ-ai
description: AI Skills for Economists - Data analysis, econometrics, LaTeX writing, and more
workflow_stage: analysis
compatibility: [claude-code, opencode, cursor, gemini-cli]
---

# Econ AI Skills

A collection of AI skills for economists to supercharge research workflows.

## Available Skills

### 📊 Data Analysis
- `stata-data-cleaning` - Clean and transform messy data in Stata
- `stata-regression` - Run regression analyses in Stata with publication-ready output
- `api-data-fetcher` - Fetch economic data from FRED, World Bank, and other APIs
- `python-panel-data` - Panel data analysis with Python using linearmodels and pandas

### 🔬 Econometric Analysis
- `r-econometrics` - Run IV, DiD, and RDD analyses in R with proper diagnostics

### 📝 Academic Writing
- `academic-paper-writer` - Draft economics papers with proper structure and academic style
- `latex-tables` - Generate publication-ready regression tables in LaTeX

### 📐 Theory & Modeling
- `latex-econ-model` - Write and typeset economic models in LaTeX with proper notation
- `general-equilibrium-model-builder` - Build and solve Walrasian general equilibrium models with Julia

### 💡 Ideation
- `research-ideation` - Generate research questions from economic phenomena

### 📚 Literature Review
- `lit-review-assistant` - Search, summarize, and synthesize economics literature

### 🎯 Communication
- `beamer-presentation` - Create academic presentations in Beamer with professional themes
- `econ-visualization` - Create publication-quality charts and graphs for economics papers

## Usage

To use a specific skill, invoke it directly:

```
/econ-ai/analysis/r-econometrics Run a DiD analysis on my treatment data
```

Or use natural language to describe what you need - the AI will use the appropriate skill.

## Installation

Skills are pre-installed in ~/.config/opencode/skills/econ-ai/

For manual installation:
```bash
mkdir -p ~/.config/opencode/skills
git clone https://github.com/meleantonio/awesome-econ-ai-stuff.git ~/.config/opencode/skills/econ-ai
```
