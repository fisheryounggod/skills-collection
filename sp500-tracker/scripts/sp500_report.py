#!/usr/bin/env python3
"""
SP500 每日报告生成脚本
- 拉取最近 ~65 交易日数据（FRED优先，yfinance备用）
- 生成4面板分析图（价格/回撤/收益率/波动率）
- 输出文字摘要 + 图片路径
"""
import os
import sys
import base64
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm

# ========== 字体配置 ==========
user_font = '/home/yxf/.fonts/NotoSansCJKsc-Regular.otf'
if os.path.exists(user_font):
    fm.fontManager.addfont(user_font)
    plt.rcParams['font.family'] = ['Noto Sans CJK SC', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ========== 颜色 ==========
C_BLUE   = '#58a6ff'
C_GREEN  = '#3fb950'
C_RED    = '#f85149'
C_YELLOW = '#d29922'
C_PURPLE = '#bc8cff'
C_GRAY   = '#8b949e'
C_BG     = '#0d1117'
C_PANEL  = '#161b22'

# ========== 数据拉取 ==========
TODAY = pd.Timestamp.today()
START = (TODAY - pd.Timedelta(days=100)).strftime('%Y-%m-%d')
END   = TODAY.strftime('%Y-%m-%d')

def fetch_data():
    """FRED优先，yfinance备用"""
    # FRED
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd={START}&coed={END}"
    try:
        df = pd.read_csv(url, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index)
        df.columns = ['Close']
        if len(df) > 10:
            print(f"[OK] FRED: {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}", file=sys.stderr)
            return df
    except Exception as e:
        print(f"[WARN] FRED failed: {e}", file=sys.stderr)

    # yfinance fallback
    try:
        import yfinance as yf
        df2 = yf.download("^GSPC", start=START, end=END, auto_adjust=True, progress=False)
        df2 = df2[['Close']]
        if len(df2) > 10:
            print(f"[OK] yfinance: {len(df2)} rows", file=sys.stderr)
            return df2
    except Exception as e:
        print(f"[ERROR] yfinance also failed: {e}", file=sys.stderr)

    return None

# ========== 核心指标 ==========
def compute_stats(price):
    returns = price.pct_change().dropna()
    first   = price.iloc[0]
    last    = price.iloc[-1]
    total_ret = (last / first - 1) * 100
    ann_ret   = ((last / first) ** (252 / len(price)) - 1) * 100 if len(price) > 0 else 0
    vol       = returns.std() * (252 ** 0.5) * 100
    std_ret = returns.std()
    std_val = float(std_ret)
    sharpe   = (returns.mean() / std_ret * (252 ** 0.5)) if std_val > 0 else 0
    roll_max  = price.expanding().max()
    dd        = (price - roll_max) / roll_max * 100
    max_dd    = dd.min()
    peak_val  = price.max()
    peak_idx  = price.idxmax()
    trough_val = price.min()
    trough_idx = price.idxmin()
    ma20      = price.rolling(20).mean()
    ma60      = price.rolling(60).mean()
    return {
        'price': price, 'returns': returns,
        'first': first, 'last': last,
        'total_ret': total_ret, 'ann_ret': ann_ret,
        'vol': vol, 'sharpe': sharpe,
        'max_dd': max_dd, 'dd': dd,
        'peak_val': peak_val, 'peak_idx': peak_idx,
        'trough_val': trough_val, 'trough_idx': trough_idx,
        'ma20': ma20, 'ma60': ma60,
    }

# ========== 绘图 ==========
def plot(s):
    price    = s['price']
    returns  = s['returns']
    total_ret = s['total_ret']
    ann_ret  = s['ann_ret']
    vol      = s['vol']
    sharpe   = s['sharpe']
    max_dd   = s['max_dd']
    dd       = s['dd']
    peak_val = s['peak_val']
    peak_idx = s['peak_idx']
    trough_val = s['trough_val']
    trough_idx = s['trough_idx']
    ma20     = s['ma20']
    ma60     = s['ma60']

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 14), facecolor=C_BG)

    # Panel 1: 价格 + MA
    ax1 = fig.add_axes([0.06, 0.68, 0.87, 0.22])
    ax1.set_facecolor(C_PANEL)
    ax1.plot(price.index, price.values, color=C_BLUE, linewidth=1.6)
    ax1.plot(ma20.index, ma20.values, color=C_YELLOW, linewidth=1.0, alpha=0.8)
    ax1.plot(ma60.index, ma60.values, color=C_PURPLE, linewidth=1.0, alpha=0.7)
    ax1.fill_between(price.index, price.values.ravel(), alpha=0.08, color=C_BLUE)
    ax1.axhline(y=s['first'], color=C_GRAY, linestyle='--', linewidth=0.8, alpha=0.6)
    ax1.text(price.index[5], s['first'] + 25, f"起始 {s['first']:,.0f}", color=C_GRAY, fontsize=8)
    ax1.set_ylabel('Index', color=C_GRAY, fontsize=9)
    ax1.set_title(f"S&P 500 走势 ({price.index[0].strftime('%Y-%m-%d')} → {price.index[-1].strftime('%Y-%m-%d')})",
                  color='white', fontsize=13, fontweight='bold', pad=10)
    ax1.tick_params(colors=C_GRAY, labelsize=8)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax1.grid(True, alpha=0.1, color=C_GRAY)
    for sp in ax1.spines.values(): sp.set_edgecolor(C_BG)

    ax1.annotate(f"高点 {peak_val:,.0f}", xy=(peak_idx, peak_val),
                  xytext=(peak_idx, peak_val + 60), color=C_GREEN, fontsize=8, ha='center',
                  arrowprops=dict(arrowstyle='->', color=C_GREEN, lw=0.8))
    ax1.annotate(f"低点 {trough_val:,.0f}", xy=(trough_idx, trough_val),
                  xytext=(trough_idx, trough_val - 60), color=C_RED, fontsize=8, ha='center',
                  arrowprops=dict(arrowstyle='->', color=C_RED, lw=0.8))
    ax1.scatter([peak_idx], [peak_val], color=C_GREEN, s=30, zorder=5)
    ax1.scatter([trough_idx], [trough_val], color=C_RED, s=30, zorder=5)

    # Panel 2: 回撤
    ax2 = fig.add_axes([0.06, 0.44, 0.87, 0.18], sharex=ax1)
    ax2.set_facecolor(C_PANEL)
    ax2.fill_between(dd.index, dd.values, 0, alpha=0.7, color=C_RED)
    ax2.plot(dd.index, dd.values, color=C_RED, linewidth=0.8)
    ax2.axhline(y=0, color=C_GRAY, linewidth=0.8)
    ax2.set_ylabel('回撤 %', color=C_GRAY, fontsize=9)
    ax2.set_title('回撤幅度', color='white', fontsize=10, pad=6)
    ax2.tick_params(colors=C_GRAY, labelsize=8)
    ax2.grid(True, alpha=0.1)
    for sp in ax2.spines.values(): sp.set_edgecolor(C_BG)
    dd_min_idx = dd.idxmin()
    ax2.scatter([dd_min_idx], [dd.min()], color=C_YELLOW, s=30, zorder=5)
    ax2.annotate(f"最大回撤 {dd.min():.1f}%", xy=(dd_min_idx, dd.min()),
                 xytext=(dd_min_idx, dd.min() - 2), color=C_YELLOW, fontsize=8, ha='center',
                 arrowprops=dict(arrowstyle='->', color=C_YELLOW, lw=0.8))

    # Panel 3: 周收益
    ax3 = fig.add_axes([0.06, 0.26, 0.87, 0.14], sharex=ax1)
    ax3.set_facecolor(C_PANEL)
    weekly = price.resample('W').last()
    weekly_ret = weekly.pct_change().dropna() * 100
    colors_w = [C_GREEN if x >= 0 else C_RED for x in weekly_ret.values]
    ax3.bar(weekly_ret.index, weekly_ret.values, width=4, color=colors_w, alpha=0.8)
    ax3.axhline(y=0, color=C_GRAY, linewidth=0.8)
    ax3.set_ylabel('周收益 %', color=C_GRAY, fontsize=9)
    ax3.set_title('周收益率', color='white', fontsize=10, pad=6)
    ax3.tick_params(colors=C_GRAY, labelsize=8)
    ax3.grid(True, alpha=0.1, axis='y')
    for sp in ax3.spines.values(): sp.set_edgecolor(C_BG)

    # Panel 4: 波动率
    ax4 = fig.add_axes([0.06, 0.08, 0.87, 0.14], sharex=ax1)
    ax4.set_facecolor(C_PANEL)
    roll_std = returns.rolling(10).std() * (252 ** 0.5) * 100
    ax4.fill_between(roll_std.index, roll_std.values, alpha=0.5, color=C_PURPLE)
    ax4.plot(roll_std.index, roll_std.values, color=C_PURPLE, linewidth=1.0)
    ax4.set_ylabel('波动率 %', color=C_GRAY, fontsize=9)
    ax4.set_title('年化波动率 (10日滚动)', color='white', fontsize=10, pad=6)
    ax4.tick_params(colors=C_GRAY, labelsize=8)
    ax4.grid(True, alpha=0.1)
    for sp in ax4.spines.values(): sp.set_edgecolor(C_BG)
    ax4.set_xlabel('')

    # Stats boxes
    c_ret = C_GREEN if total_ret >= 0 else C_RED
    fig.text(0.735, 0.975, f"总收益 {total_ret:+.2f}%", color=c_ret,
             fontsize=11, fontweight='bold', va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=C_PANEL, edgecolor=C_BLUE, alpha=0.9))
    fig.text(0.84, 0.975, f"年化 {ann_ret:+.2f}%", color=C_BLUE, fontsize=10, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=C_PANEL, edgecolor=C_BLUE, alpha=0.9))
    fig.text(0.735, 0.94, f"波动率 {vol:.1f}%", color=C_YELLOW, fontsize=10, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=C_PANEL, edgecolor=C_YELLOW, alpha=0.9))
    fig.text(0.84, 0.94, f"夏普 {sharpe:.2f}", color=C_PURPLE, fontsize=10, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=C_PANEL, edgecolor=C_PURPLE, alpha=0.9))
    fig.text(0.735, 0.905, f"最大回撤 {max_dd:.2f}%", color=C_RED, fontsize=10, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=C_PANEL, edgecolor=C_RED, alpha=0.9))

    out = '/tmp/sp500_daily_report.png'
    plt.savefig(out, dpi=180, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    return out

# ========== 文字摘要 ==========
def summary(s, n_days):
    p   = s['price']
    ret = s['returns']
    monthly = p.resample('ME').last()
    mr = monthly.pct_change().dropna() * 100

    lines = [
        f"📈 S&P 500 投资追踪",
        f"━━━━━━━━━━━━━━━━",
        f"📊 数据区间：{p.index[0].strftime('%Y-%m-%d')} → {p.index[-1].strftime('%Y-%m-%d')}（{n_days}个交易日）",
        f"",
        f"💰 价格：{s['first']:,.2f} → {s['last']:,.2f}  ({s['total_ret']:+.2f}%)",
        f"📐 年化收益：{s['ann_ret']:+.2f}%  波动率：{s['vol']:.1f}%  夏普：{s['sharpe']:.2f}",
        f"📉 最大回撤：{s['max_dd']:.2f}%  当前回撤：{(s['last']/s['peak_val']-1)*100:.2f}%",
        f"",
        f"📅 月度涨跌：",
    ]
    for dt, r in mr.items():
        sign = "▲" if r >= 0 else "▼"
        lines.append(f"   {dt.strftime('%Y年%m月')} {sign} {abs(r):.2f}%")

    lines += [
        "",
        f"⏱️ 更新：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    return "\n".join(lines)

# ========== 主程序 ==========
def main():
    df = fetch_data()
    if df is None:
        print("[ERROR] No data available", file=sys.stderr)
        sys.exit(1)

    price = df['Close']
    s = compute_stats(price)

    img_path = plot(s)
    text = summary(s, len(price))

    # 输出图片路径（供调用方读取）
    print(img_path)
    # 输出文字摘要（stderr或stdout）
    print(text, file=sys.stderr)

if __name__ == '__main__':
    main()
