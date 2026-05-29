---
name: sector-fund-flow-video-v2
description: A股板块主力资金流视频生成流水线v2。从东方财富API拉取22个板块实时数据，生成竖屏9:16动画MP4推送到微信。
triggers:
  - 主力资金视频v2
  - 板块资金流视频v2
  - sector fund flow v2
category: content
version: 2.0.0
---

# Sector Fund Flow Video Pipeline v2

A股板块主力资金流视频生成 → 微信发送全流程（22色全色轮 + 方框标签 + 1位小数 + 日期标题）。

## 路径速查

- CSV数据：`/Users/mac/Downloads/Data/sector_data/`
- 视频输出：`/Users/mac/Downloads/主力资金数据/`
- 动画引擎：`/Users/mac/Downloads/Data/animation_player.py`

> ⚠️ **执行环境注意**：终端默认 venv 无 pandas。数据拉取和视频生成**必须通过 `execute_code` 调用 `/usr/bin/python3`**（系统Python有完整数据科学栈）。详见 `references/execution-guide.md`。

## 1. 数据拉取

**直接调用 API，不走 eastmoney_sector_flow.py**（脚本 secid 映射不全导致化工/医疗数据永远是旧数据）。

```python
import urllib.request, ssl, json, pandas as pd, os

ctx = ssl.create_default_context()
ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

SECTORS = {
    '存储芯片':'90.BK1137','电网设备':'90.BK0457','云计算':'90.BK0579',
    '人工智能':'90.BK0800','半导体材料设备':'90.BK1326','消费电子':'90.BK1037',
    'CPO':'90.BK1128','通信':'90.BK1215','半导体':'90.BK1036',
    '电力':'90.BK0428','大科技':'90.BK0891','光伏':'90.BK1031',
    '国产算力':'90.BK1134','先进制造':'90.BK1237','军工':'90.BK0490',
    '商业航天':'90.BK0963','AI应用':'90.BK1629','油气资源':'90.BK1649',
    '有色金属':'90.BK0478','医疗器械':'90.BK1045','医疗服务':'90.BK1044',
    '医药生物':'90.BK1043'
}

DATA_DIR = '/Users/mac/Downloads/Data/sector_data/'
os.makedirs(DATA_DIR, exist_ok=True)

results = []
for name, secid in SECTORS.items():
    url = (f'https://push2delay.eastmoney.com/api/qt/stock/fflow/kline/get'
           f'?lmt=0&klt=1&secid={secid}'
           f'&fields1=f1,f2,f3,f7'
           f'&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63')
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://data.eastmoney.com/'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        data = json.loads(resp.read())
        klines = data.get('data',{}).get('klines',[])
        if klines:
            rows = [{'time':k.split(',')[0],'sector':name,
                     'mainForce':float(k.split(',')[1]),'small':float(k.split(',')[2]),
                     'medium':float(k.split(',')[3]),'large':float(k.split(',')[4]),
                     'superLarge':float(k.split(',')[5])} for k in klines]
            pd.DataFrame(rows).to_csv(f'{DATA_DIR}{name}_fund_flow.csv', index=False, encoding='utf-8-sig')
            last = klines[-1].split(',')
            mf = float(last[1])/1e8
            results.append((name, last[0], mf))
    except Exception as e:
        print(f'❌ {name}: {e}')
```

## 2. 视频生成（v2 标准）

### 2.1 分时对比视频（竖屏 9:16）

```python
import pandas as pd, matplotlib.pyplot as plt, matplotlib.animation as animation, matplotlib, numpy as np
from datetime import datetime
matplotlib.use('Agg')
plt.rcParams['axes.unicode_minus'] = False
import matplotlib.font_manager as fm, os

# 动态查找系统可用中文字体（Microsoft YaHei 在 macOS 不存在，必须探测）
_font_found = False
for _fp in ['/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/Library/Fonts/Arial Unicode.ttf']:
    if os.path.exists(_fp):
        fm.fontManager.addfont(_fp)
        _fname = fm.FontProperties(fname=_fp).get_name()
        plt.rcParams['font.sans-serif'] = [_fname] + plt.rcParams['font.sans-serif']
        print(f'字体: {_fname}')
        _font_found = True
        break
if not _font_found:
    # 最后兜底：让 matplotlib 自行选择可显示中文的字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC'] + plt.rcParams['font.sans-serif']

# 22色全色轮，无重复色相
sectors_info = [
    ('存储芯片',    '#FF4757'),('大科技',      '#FF7F50'),('先进制造',    '#FF9800'),
    ('半导体',      '#FFC107'),('半导体材料设备','#FFEB3B'),('油气资源',    '#C0E040'),
    ('商业航天',    '#8BC34A'),('人工智能',    '#4CAF50'),('电网设备',    '#009688'),
    ('云计算',      '#00BCD4'),('通信',        '#03A9F4'),('CPO',         '#2979FF'),
    ('消费电子',    '#5C6BC0'),('AI应用',      '#7E57C2'),('军工',        '#AB47BC'),
    ('医疗服务',    '#EC407A'),('医疗器械',    '#F06292'),('电力',        '#EF5350'),
    ('光伏',        '#FF7043'),('国产算力',    '#26A69A'),('有色金属',    '#78909C'),
    ('医药生物',    '#B0BEC5'),
]

DATA_DIR = '/Users/mac/Downloads/Data/sector_data/'
OUTPUT = '/Users/mac/Downloads/主力资金数据/'
import os; os.makedirs(OUTPUT, exist_ok=True)
today = datetime.now().strftime('%Y-%m-%d')  # 视频标题用当天日期
# 注意：东方财富数据在非交易日返回最近交易日数据，因此实际数据日期可能≠今天。
# 视频文件名和标题均使用 datetime.now()，数据内的时间戳用于"截至"脚注。
dfs = {}
for n, _ in sectors_info:
    df = pd.read_csv(f'{DATA_DIR}{n}_fund_flow.csv')
    df['mainForce'] = df['mainForce'] / 1e8
    dfs[n] = df

times = dfs['存储芯片']['time'].tolist()
N = len(times)

# 按最新值排序
latest = {n: dfs[n]['mainForce'].iloc[-1] for n,_ in sectors_info}
sorted_sectors = sorted(sectors_info, key=lambda x: latest[x[0]], reverse=True)

all_vals = np.concatenate([dfs[n]['mainForce'].values for n,_ in sectors_info])
y_min, y_max = all_vals.min(), all_vals.max()
y_margin = (y_max - y_min) * 0.15

from matplotlib.ticker import FuncFormatter
def y_fmt(x, pos=None): return f'{int(x)}亿'
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
    ax.set_title(f'主力资金板块分时流向对比  {today}', color='white', fontsize=14, fontweight='bold', pad=10)

    idx = min(frame, N-1)
    for name, color in sorted_sectors:
        df = dfs[name]
        mf_s = df['mainForce'].iloc[:idx+1].values
        ax.plot(np.arange(len(mf_s)), mf_s, color=color, linewidth=1.4, alpha=0.85)
        last_val = mf_s[-1]
        sign = '+' if last_val >= 0 else ''
        label_text = f'{name} {sign}{last_val:.1f}'
        ax.annotate(label_text,
                    xy=(len(mf_s)-1, last_val),
                    xytext=(len(mf_s)+1, last_val),
                    color='white', fontsize=8, va='center', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.85, edgecolor='none'),
                    arrowprops=dict(arrowstyle='->', color=color, alpha=0.6))

    ax.text(0.5, -0.06, f'截至 {times[idx]}', transform=ax.transAxes, color='#888', fontsize=9, ha='center')

ani = animation.FuncAnimation(fig, update, frames=N, blit=False, interval=200)
save_path = f'{OUTPUT}{today}_主力资金分时对比_label.mp4'
ani.save(save_path, writer='ffmpeg', fps=5, dpi=DPI, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
plt.close()
print(f'✅ 视频已生成: {save_path}')
```

### 2.2 动态条形图视频（竖屏 9:16）

```python
# 22个板块同步滚动，绿色净流入/红色净流出，1080×1920
# 注意：v2版本已停用，改用分时对比图
```

## 3. 竖屏参数速查

| 参数 | 值 |
|------|-----|
| 宽度×高度 | 1080×1920 |
| DPI | 120 |
| figsize | `(9, 16)` |
| fps | 5 |
| interval/帧 | 200ms |
| codec | libx264 |
| ffmpeg extra_args | `['-pix_fmt', 'yuv420p']` |

## 4. 微信发送

**当前状态：iLink rate limit 拦截，发送失败率极高。**

- 微信 DM `o9cq802nxSy8F1d7Vc65-XgAe83E` 和 `o9cq801rqSFjl8od4ss5V3u01M2w` 均受 rate limit 影响
- `send_message(target='weixin:...')` 调用 iLink，会被限流拦截，**不建议在自动化流程中使用**
- **手动方案**：视频保存在 `/Users/mac/Downloads/主力资金数据/`，需手动发送
- **自动方案**：itchat/wxpy 在 headless cron 环境无法扫码登录，所有方案均失败
- 若需自动发送，考虑用 Telegram（需配置 home channel）或换用其他推送渠道

## 5. 输出目录

- CSV：`/Users/mac/Downloads/Data/sector_data/`
- 视频：`/Users/mac/Downloads/主力资金数据/`
- 命名规范：`2026-05-18_主力资金分时对比_label.mp4`

## 6. 已知陷阱

### 中文字体必须动态探测
`Microsoft YaHei` 在 macOS 上**不存在**，直接写会导致所有中文显示为空白方块。必须用 `matplotlib.font_manager` 遍历探测 STHeiti/Arial Unicode 等系统字体。上方代码块已内置此逻辑，直接复制使用即可。

### 视频生成必须用 `/usr/bin/python3`
`execute_code` 调用的 Python 虚拟环境没有 pandas/matplotlib。数据拉取和视频生成都需要通过 `terminal(background=false)` 调用**系统 Python** `/usr/bin/python3`。

### 医疗服务板块偶发超时
东方财富 `push2delay.eastmoney.com` 对单个板块请求可能报 `Remote end closed connection`。需重试或容忍 21/22 的少量缺失。

## 7. v2 视觉标准

- **22色全色轮**：红→橙→黄→绿→青→蓝→紫→粉，无重复色相
- **方框标签**：白色文字 + 颜色填充圆角矩形
- **数字**：保留1位小数（如 `+63.2`）
- **标题**：含当天日期 `主力资金板块分时流向对比  2026-05-18`
- **纵坐标**：刻度显示整数+"亿"（如 `50亿`、`0亿`、`-50亿`）