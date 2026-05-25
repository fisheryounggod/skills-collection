---
name: sp500-data-fetcher
description: >-
  Fetch S&P 500 historical data for analysis and visualization.
  Primary source: Yahoo Finance (yfinance). Fallback: FRED (Federal Reserve).
  Covers data fetching, key stats computation, and trend visualization.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [finance, sp500, data, matplotlib, analysis]
    category: data-science
---

# S&P 500 Data Fetcher

Fetch S&P 500 historical price data, compute key statistics, and generate trend charts.

## Data Sources

| Source | Pros | Cons |
|--------|------|------|
| **yfinance** | Full OHLCV, real-time | Rate-limited, can fail |
| **FRED** (Federal Reserve) | Always available, free | Close price only, daily |

**Rule:** Try yfinance first. If rate-limited or fails, fall back to FRED.

## Quick Start

```python
import pandas as pd
import matplotlib.pyplot as plt

# === Load Data ===

# Option 1: yfinance (preferred)
import yfinance as yf
sp500 = yf.download("^GSPC", start="2016-01-20", auto_adjust=True)
# Note: auto_adjust=True avoids some column naming issues

# Option 2: FRED fallback (2026-04 verified working)
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2016-01-20&coed=2026-04-22"
df = pd.read_csv(url, index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index)
df.columns = ['Close']
```

## Key Statistics

```python
price = df['Close']
returns = price.pct_change().dropna()

first_price = price.iloc[0]
last_price = price.iloc[-1]
total_return = (last_price / first_price - 1) * 100
annualized = ((last_price / first_price) ** (252 / len(price)) - 1) * 100
volatility = returns.std() * (252 ** 0.5) * 100
max_dd = ((price - price.expanding().max()) / price.expanding().max()).min() * 100
```

## Visualization Template (3-panel dark theme)

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.style.use('dark_background')

fig, axes = plt.subplots(3, 1, figsize=(16, 12), facecolor='#1a1a2e')

# Panel 1: Price
ax1 = axes[0]
ax1.set_facecolor('#16213e')
ax1.plot(price.index, price.values, color='#00d4ff', linewidth=1.2)
ax1.fill_between(price.index, price.values, alpha=0.15, color='#00d4ff')
ax1.set_title('S&P 500 Price Index')
ax1.grid(True, alpha=0.15)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator())

# Panel 2: Drawdown
ax2 = axes[1]
ax2.set_facecolor('#16213e')
rolling_max = price.expanding().max()
drawdown = (price - rolling_max) / rolling_max * 100
ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.7, color='#ff6b6b')
ax2.set_title('Drawdown from Peak')
ax2.grid(True, alpha=0.15)

# Panel 3: Annual Returns
ax3 = axes[2]
ax3.set_facecolor('#16213e')
annual_prices = price.resample('YE').last()
annual_returns = annual_prices.pct_change().dropna() * 100
colors = ['#51cf66' if x >= 0 else '#ff6b6b' for x in annual_returns.values]
ax3.bar(annual_returns.index.year, annual_returns.values, color=colors, alpha=0.8)
ax3.set_title('Annual Returns (%)')
ax3.grid(True, alpha=0.15, axis='y')

plt.tight_layout()
plt.savefig('/tmp/sp500_trend.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()
```

## Pitfalls

1. **yfinance rate limiting**: `YFRateLimitError: Too Many Requests` — wait 30s+ or switch to FRED
2. **FRED date range**: use `cosd` (start) and `coed` (end) params in URL; only has closing price
3. **yfinance column names**: `auto_adjust=True` collapses `Adj Close` → `Close`, avoids multi-level columns
4. **FRED data starts later than requested**: FRED SP500 series starts 2016-04-22 despite 2016-01-20 request
5. **execute_code vs Jupyter**: yfinance works in `execute_code`, Jupyter kernel approach failed due to XSRF token issues
6. **FRED `read_csv` has no `timeout` param**: never pass `timeout=15` to `pd.read_csv` for FRED URL
7. **Pandas `.std()` in boolean context**: `if returns.std() > 0` raises `ValueError: truth value of Series is ambiguous` — assign to variable first: `std = returns.std(); sharpe = ... if std > 0 else 0`
8. **`matplotlib.dates.WeekLocator` does not exist**: use `mdates.AutoDateLocator()` or `mdates.WeekdayLocator()` instead
9. **Chinese font not found in matplotlib**: must call `fm.fontManager.addfont(path)` before using; set `plt.rcParams['font.family'] = ['Noto Sans CJK SC', 'sans-serif']` and `plt.rcParams['axes.unicode_minus'] = False`
10. **Chinese font path on this system**: `/home/yxf/.fonts/NotoSansCJKsc-Regular.otf` (also available: `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`)

## 4-Panel Dark Theme Template (Chinese, verified 2026-04)

```python
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import yfinance as yf

# === 中文字体配置（必须在任何绘图前执行）===
user_font = '/home/yxf/.fonts/NotoSansCJKsc-Regular.otf'
if os.path.exists(user_font):
    fm.fontManager.addfont(user_font)
    plt.rcParams['font.family'] = ['Noto Sans CJK SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# === 数据获取：FRED优先，yfinance备用 ===
url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd={START}&coed={END}"
try:
    df = pd.read_csv(url, index_col=0, parse_dates=True)  # 注意：无timeout参数
    df.index = pd.to_datetime(df.index)
    df.columns = ['Close']
except Exception:
    df = yf.download("^GSPC", start=START, end=END, auto_adjust=True)[['Close']]

price = df['Close']
returns = price.pct_change().dropna()

# === 核心指标 ===
std = returns.std()  # 先赋值，避免布尔上下文歧义
sharpe = (returns.mean() / std * (252 ** 0.5)) if std > 0 else 0

# === 4面板绘图 ===
C_BLUE='#58a6ff'; C_GREEN='#3fb950'; C_RED='#f85149'
C_YELLOW='#d29922'; C_PURPLE='#bc8cff'; C_GRAY='#8b949e'
C_BG='#0d1117'; C_PANEL='#161b22'

plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 14), facecolor=C_BG)

ax1 = fig.add_axes([0.06, 0.68, 0.87, 0.22])
ax1.set_facecolor(C_PANEL)
ax1.plot(price.index, price.values, color=C_BLUE, linewidth=1.6)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax1.xaxis.set_major_locator(mdates.AutoDateLocator())  # 不要用WeekLocator
# ... (完整代码见 sp500-tracker/scripts/sp500_report.py)

plt.savefig('/tmp/sp500_report.png', dpi=180, bbox_inches='tight', facecolor=C_BG)
plt.close()
```

## Status

- FRED URL pattern verified 2026-04: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd={start}&coed={end}`
- yfinance v1.3.0 with curl-cffi — rate limiting is the main failure mode
- Chinese font (Noto Sans CJK SC) confirmed rendering correctly on 2026-04-25
- 4-panel chart template working with sharpe ratio, drawdown, weekly returns, rolling volatility
