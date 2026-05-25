---
name: sp500-tracker
title: S&P 500 投资追踪
description: 每个交易日收盘后自动拉取SP500数据，生成多面板分析图表（价格/回撤/收益/波动率），中文报告推送到微信。FRED数据源，无需API Key。
category: finance
tags: [sp500, 美股, 投资, 图表, 追踪, 自动化]
trigger: ["SP500", "美股追踪", "标普500", "sp500 tracker", "股市日报"]
---

# S&P 500 投资追踪 Skill

每个交易日 22:00 自动拉取 S&P 500 数据，生成4面板分析图表，文字摘要推送到微信。

## 数据源

| 源 | 优点 | 缺点 |
|---|---|---|
| **FRED** (优先) | 免费、无需API Key、稳定 | 只有收盘价，日级 |
| **yfinance** (备用) | 完整OHLCV | 可能限流 |

## 输出内容

### 图表（4面板，深色主题）
1. **价格走势** — 价格线 + MA20 + MA60 + 标注高低点
2. **回撤幅度** — 相对历史高点的回撤百分比
3. **收益率** — 周度收益率柱状图
4. **波动率** — 10日滚动年化波动率

### 文字摘要
- 起始 → 结束价格及涨跌幅
- 年化收益率 / 波动率 / 夏普比率
- 最大回撤 / 当前回撤
- 月度涨跌（当月）

## 字体配置

```python
import matplotlib.font_manager as fm
user_font = '/home/yxf/.fonts/NotoSansCJKsc-Regular.otf'
fm.fontManager.addfont(user_font)
plt.rcParams['font.family'] = ['Noto Sans CJK SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
```

## 脚本

路径：`scripts/sp500_report.py`

## 已知 Bug 与修复

### matplotlib fill_between 维度错误
**问题**：`DataFrame['Close'].values` 返回 shape `(n,1)` 的2D数组，但 `fill_between` 需要1D数组。
**错误**：`ValueError: 'y1' is not 1-dimensional`
**修复**：使用 `.ravel()` 展平：
```python
ax1.fill_between(price.index, price.values.ravel(), alpha=0.08, color=C_BLUE)
```

## Cron 定时任务

- **时间**：每个交易日 22:00 (`0 22 * * 1-5`)
- **启动**：先 `source ~/.hermes/scripts/hermes-env.sh` 再运行脚本
- **推送**：图片 + 文字摘要发送到微信

## 微信推送机制

> ⚠️ `send_message(target='weixin')` 需要在 `~/.hermes/config.yaml` 中配置微信平台凭证。当前环境平台未配置，导致推送静默失败。

本机环境（确认）：
- WeChat.app 和 WeChat2.app 已安装在 `/Applications/`
- `imsg` CLI 可用（但仅支持 iMessage，不支持微信）
- 图片输出路径：`/tmp/sp500_daily_report.png`

**待解决**：配置微信推送凭证，或改用 AppleScript/GUI 自动化方式向微信窗口发送图片。
  -e 'activate' \
  -e 'end tell'
# 然后通过剪贴板 + AppleScript 粘贴发送
```

**注意**：本机安装了 WeChat.app 和 WeChat2.app，发送时注意选择正确的应用名称。

## 关键参数

| 参数 | 值 |
|------|---|
| 数据范围 | 最近65个交易日（约3个月） |
| 图表尺寸 | 16×14 inch, 180 dpi |
| 图表背景 | 深色 (#0d1117) |
| 字体 | Noto Sans CJK SC |
| 图片路径 | `/tmp/sp500_daily_report.png` |

## 注意事项

- FRED 数据通常在交易日 16:00 ET 后更新，22:00 时数据已就绪
- yfinance 备用逻辑：FRED 失败时自动切换
- 图片通过 `MEDIA:/path/to/img.png` 格式发送
- 波动率计算：10日滚动标准差 × √252
