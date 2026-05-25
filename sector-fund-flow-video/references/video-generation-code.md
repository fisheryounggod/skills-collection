# A股主力资金流视频生成参考代码

## 单板块视频（横屏）

使用 `animation_player.py`：
```python
from animation_player import play_capital_flow_animation
mp4 = play_capital_flow_animation(df, '板块名', '/path/to/output.mp4')
```

## 多板块竖屏动态条形图（9:16, 1080×1920）

> ⚠️ 条形图颜色约定：流入绿色 / 流出红色（与时序图相反）

完整可运行脚本：
```python
import pandas as pd, matplotlib.pyplot as plt, matplotlib.animation as animation, numpy as np, matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

sectors_info = [
    ('存储芯片','#22c55e'),('大科技','#22c55e'),('先进制造','#22c55e'),
    ('半导体','#22c55e'),('半导体材料设备','#a855f7'),('油气资源','#06b6d4'),
    ('商业航天','#14b8a6'),('人工智能','#84cc16'),
    ('云计算','#ef4444'),('军工','#f97316'),('消费电子','#fb923c'),
    ('CPO','#fdba74'),('通信','#fed7aa'),('电力','#fca5a5'),
    ('光伏','#f87171'),('国产算力','#dc2626'),('AI应用','#b91c1c'),
    ('有色金属','#7f1d1d'),('医疗器械','#991b1b'),('医疗服务','#b91c1b'),('医药生物','#991b1b')
]

dfs = {name: pd.read_csv(f'sector_data/{name}_fund_flow.csv') for name, _ in sectors_info}
times = dfs['存储芯片']['time'].tolist()
N = len(times)

W, H, DPI = 1080, 1920, 120
fig, ax = plt.subplots(figsize=(W/DPI, H/DPI), dpi=DPI)
fig.patch.set_facecolor('#0f0f23'); ax.set_facecolor('#0f0f23')

def update(frame):
    ax.cla()
    ax.set_xlim(-100, 130); ax.set_ylim(-1, len(sectors_info))
    ax.set_yticks([]); ax.spines[:].set_color('#222')
    ax.tick_params(colors='white', labelsize=9)
    ax.grid(True, alpha=0.08, color='white', axis='x')
    ax.axvline(0, color='white', linewidth=0.5)
    ax.set_xlabel('主力净流入（亿元）', fontsize=10, color='#aaa')
    t = times[min(frame, N-1)]
    t_only = t.split(' ')[1] if ' ' in t else t
    for i, (name, color) in enumerate(sectors_info):
        mf = dfs[name]['mainForce'].iloc[min(frame, len(dfs[name])-1)]
        bar_color = '#22c55e' if mf >= 0 else '#ef4444'
        ax.barh(i, mf, height=0.55, color=bar_color, alpha=0.85)
        ax.text(-3, i, name, va='center', ha='right', fontsize=9.5, color='#ccc')
        ax.text(mf+(2 if mf>=0 else -2), i, f'{mf:.1f}', va='center',
               ha='left' if mf>=0 else 'right', fontsize=9, color='white')
    ax.set_title('主力资金板块动态', color='white', fontsize=15, fontweight='bold', pad=12)
    ax.text(0.5, -0.06, f'截至 {t_only}', transform=ax.transAxes, color='#888', fontsize=9, ha='center')

ani = animation.FuncAnimation(fig, update, frames=N, blit=False, interval=150)
ani.save('/Users/mac/Downloads/主力资金数据/2026-05-18_主力资金动态_9x16.mp4',
         writer='ffmpeg', fps=8, dpi=DPI, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
plt.close()
```

## 多板块分时时序图（9:16, 1080×1920，标签随曲线末端移动+方框）

> ⚠️ **颜色约定**：流入红色系 / 流出绿色系（与条形图相反）

> ⚠️ **单位陷阱**：CSV 存储的是原始值（元），视频生成时必须除以 `1e8` 转为"亿"，否则数字显示为几十亿。

```python
import pandas as pd, matplotlib.pyplot as plt, matplotlib.animation as animation, numpy as np, matplotlib
from matplotlib.ticker import FuncFormatter
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 颜色：流入红系 / 流出绿系，各板块颜色差异增强
sectors_info = [
    ('存储芯片','#ff2d2d'),('大科技','#ff6b35'),('先进制造','#ff9500'),
    ('半导体','#ffb347'),('半导体材料设备','#ff5e3a'),('油气资源','#ff69b4'),
    ('商业航天','#ce93d8'),('人工智能','#ef9a9a'),
    ('云计算','#00e676'),('军工','#00c853'),('消费电子','#69f0ae'),
    ('CPO','#b9f6ca'),('通信','#a7ffeb'),('电力','#64ffda'),
    ('光伏','#1de9b6'),('国产算力','#00bfa5'),('AI应用','#009688'),
    ('有色金属','#00897b'),('医疗器械','#00796b'),('医疗服务','#004d40'),('医药生物','#00695c')
]

# ⚠️ 必须除以 1e8 转换为"亿"
dfs = {}
for n, _ in sectors_info:
    df = pd.read_csv(f'sector_data/{n}_fund_flow.csv')
    df['mainForce'] = df['mainForce'] / 1e8
    dfs[n] = df

times = dfs['存储芯片']['time'].tolist()
N = len(times)

# 按最新主力净流入降序，固定板块顺序
latest = {n: dfs[n]['mainForce'].iloc[-1] for n,_ in sectors_info}
sorted_sectors = sorted(sectors_info, key=lambda x: latest[x[0]], reverse=True)

# 全局y轴范围（避免曲线越界）
all_vals = np.concatenate([dfs[n]['mainForce'].values for n,_ in sectors_info])
y_min, y_max = all_vals.min(), all_vals.max()
y_margin = (y_max - y_min) * 0.15

# 纵坐标格式化：显示"亿"单位
def y_fmt(x, pos=None):
    return f'{int(x)}亿'
formatter = FuncFormatter(y_fmt)

W, H, DPI = 1080, 1920, 120
fig, ax = plt.subplots(figsize=(W/DPI, H/DPI), dpi=DPI)
fig.patch.set_facecolor('#0f0f23'); ax.set_facecolor('#0f0f23')

def update(frame):
    ax.cla()
    ax.set_xlim(0, N-1)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    ax.yaxis.set_major_formatter(formatter)
    tick_step = max(1, N // 6)
    tick_labels = [times[i].split(' ')[1] if ' ' in times[i] else times[i] for i in range(0, N, tick_step)]
    ax.set_xticks(list(range(0, N, tick_step)))
    ax.set_xticklabels(tick_labels, fontsize=8, color='#aaa')
    ax.axhline(0, color='white', linewidth=0.8, alpha=0.4)
    ax.spines[:].set_color('#333')
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, alpha=0.08, color='white', axis='y')
    ax.set_title('主力资金板块分时流向对比', color='white', fontsize=14, fontweight='bold', pad=10)

    idx = min(frame, N-1)
    for name, color in sorted_sectors:
        df = dfs[name]
        mf_s = df['mainForce'].iloc[:idx+1].values
        ax.plot(np.arange(len(mf_s)), mf_s, color=color, linewidth=1.4, alpha=0.85)

        last_val = mf_s[-1]
        sign = '+' if last_val >= 0 else ''
        # 保留1位小数，省略"亿"单位在标签中
        label_text = f'{name} {sign}{last_val:.1f}'
        ax.annotate(label_text,
                    xy=(len(mf_s)-1, last_val),
                    xytext=(len(mf_s)+1, last_val),
                    color='white', fontsize=8, va='center', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.85, edgecolor='none'),
                    arrowprops=dict(arrowstyle='->', color=color, alpha=0.6))

    ax.text(0.5, -0.06, f'截至 {times[idx]}', transform=ax.transAxes, color='#888', fontsize=9, ha='center')

ani = animation.FuncAnimation(fig, update, frames=N, blit=False, interval=200)
ani.save('/Users/mac/Downloads/主力资金数据/2026-05-18_主力资金分时对比_label.mp4',
         writer='ffmpeg', fps=5, dpi=DPI, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
plt.close()
```

## 竖屏参数速查

| 参数 | 值 |
|------|-----|
| 宽度 | 1080 |
| 高度 | 1920 |
| DPI | 120 |
| figsize | (9, 16) |
| fps | 8（条形图）/ 5（时序图） |
| interval | 150ms/帧（条形图）/ 200ms/帧（时序图） |
| codec | libx264 |
| ffmpeg extra_args | `['-pix_fmt', 'yuv420p']` |

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 中文方块 | 缺少 `plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']` | 必须在 import pyplot 前设置 |
| 数字显示几十亿 | CSV 存储原始值，读取时未除以 `1e8` | `df['mainForce'] = df['mainForce'] / 1e8` |
| 标签数值过长 | 用 `f'{last_val}'` 显示完整浮点数 | 用 `int(last_val)` 或 `f'{last_val:.1f}'` |
| ffmpeg 报错 | `Unable to choose an output format` | 确保路径以 `.mp4` 结尾 |
| 时序图曲线贴边 | y轴范围太小 | 用 `y_min - margin ~ y_max + margin` |
