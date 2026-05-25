---
name: sector-fund-flow-video
description: A股板块主力资金流视频生成流水线。从东方财富API拉取实时数据，生成动画MP4推送微信。覆盖22个核心板块，支持横屏单板块/竖屏多板块动态条形图/时序图。
triggers:
  - "主力资金视频"
  - "板块资金流"
  - "主力资金动态"
  - "板块排行视频"
  - "sector fund flow"
category: content
tags: [a股, 资金流, 视频生成, 东方财富, animation, 9x16, 竖屏]
version: 1.3.0
---

# Sector Fund Flow Video Pipeline

A股板块主力资金流视频生成 → 微信发送全流程。

## 路径速查

- CSV数据：`/Users/mac/Downloads/Data/sector_data/`
- 视频输出：`/Users/mac/Downloads/主力资金数据/`
- 动画引擎：`/Users/mac/Downloads/Data/animation_player.py`

---

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

os.makedirs('sector_data', exist_ok=True)
for name, secid in SECTORS.items():
    url = (f'https://push2delay.eastmoney.com/api/qt/stock/fflow/kline/get'
           f'?lmt=0&klt=1&secid={secid}'
           f'&fields1=f1,f2,f3,f7'
           f'&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63')
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://data.eastmoney.com/'})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    data = json.loads(resp.read())
    klines = data.get('data',{}).get('klines',[])
    if klines:
        rows = [{'time':k.split(',')[0],'sector':name,
                 'mainForce':float(k.split(',')[1]),'small':float(k.split(',')[2]),
                 'medium':float(k.split(',')[3]),'large':float(k.split(',')[4]),
                 'superLarge':float(k.split(',')[5])} for k in klines]
        pd.DataFrame(rows).to_csv(f'sector_data/{name}_fund_flow.csv', index=False, encoding='utf-8-sig')
        print(f'✅ {name}: {klines[-1].split(",")[0]} 主力={float(klines[-1].split(",")[1])/1e8:.2f}亿')
```

> ⚠️ **已废弃**：请使用 [sector-fund-flow-video-v2](../sector-fund-flow-video-v2/SKILL.md)，本版仅作参考。
> ⚠️ 化工原料 secid 是 `90.BK0711`（注意不是 BK 开头），医疗三板块：医疗器械 `90.BK1045`、医疗服务 `90.BK1044`、医药生物 `90.BK1043`。

---

## 2. 视频生成

### 2.1 单板块视频（横屏）
使用 `animation_player.py`：
```python
from animation_player import play_capital_flow_animation
df = pd.read_csv(f'sector_data/{板块名}_fund_flow.csv')
mp4 = play_capital_flow_animation(df, '板块名', '/path/to/output.mp4')
```

### 2.2 多板块动态条形图（竖屏 9:16）
22个板块同步滚动，绿色净流入/红色净流出，1080×1920：
```python
import pandas as pd, matplotlib.pyplot as plt, matplotlib.animation as animation, matplotlib
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
dfs = {n: pd.read_csv(f'sector_data/{n}_fund_flow.csv') for n,_ in sectors_info}
times = dfs['存储芯片']['time'].tolist(); N = len(times)
W, H, DPI = 1080, 1920, 120
fig, ax = plt.subplots(figsize=(W/DPI, H/DPI), dpi=DPI)
fig.patch.set_facecolor('#0f0f23'); ax.set_facecolor('#0f0f23')

def update(frame):
    ax.cla(); ax.set_xlim(-100,130); ax.set_ylim(-1,len(sectors_info))
    ax.set_yticks([]); ax.spines[:].set_color('#222')
    ax.tick_params(colors='white',labelsize=9)
    ax.grid(True,alpha=0.08,color='white',axis='x'); ax.axvline(0,color='white',linewidth=0.5)
    ax.set_xlabel('主力净流入（亿元）',fontsize=10,color='#aaa')
    t = times[min(frame,N-1)]
    for i,(name,_) in enumerate(sectors_info):
        mf = dfs[name]['mainForce'].iloc[min(frame,len(dfs[name])-1)]
        ax.barh(i,mf,height=0.55,color='#22c55e' if mf>=0 else '#ef4444',alpha=0.85)
        ax.text(-3,i,name,va='center',ha='right',fontsize=9.5,color='#ccc')
        ax.text(mf+(2 if mf>=0 else -2),i,f'{mf:.1f}',va='center',
               ha='left' if mf>=0 else 'right',fontsize=9,color='white')
    ax.set_title('主力资金板块动态',color='white',fontsize=15,fontweight='bold',pad=12)
    ax.text(0.5,-0.06,f'截至 {t.split(" ")[1]}',transform=ax.transAxes,color='#888',fontsize=9,ha='center')

ani = animation.FuncAnimation(fig,update,frames=N,blit=False,interval=150)
ani.save('/Users/mac/Downloads/主力资金数据/2026-05-18_主力资金动态_9x16.mp4',
         writer='ffmpeg',fps=8,dpi=DPI,codec='libx264',extra_args=['-pix_fmt','yuv420p'])
plt.close()
```

### 2.3 多板块分时时序图（竖屏 9:16）
22条曲线同步滚动，实时显示所有板块主力资金轨迹。

**⚠️ 关键：读取 CSV 时必须除以 1e8 转换为"亿"**
API 返回原始值（元），CSV 直接存储原始值，视频生成脚本读取时必须除以 1e8：
```python
dfs = {}
for n, _ in sectors_info:
    df = pd.read_csv(f'{DATA_DIR}{n}_fund_flow.csv')
    df['mainForce'] = df['mainForce'] / 1e8  # ← 必须！否则数字显示为几十亿
    dfs[n] = df
```

**颜色约定：流入红系，流出绿系，各板块颜色差异增强**
```python
sectors_info = [
    ('存储芯片','#ff2d2d'),('大科技','#ff6b35'),('先进制造','#ff9500'),
    ('半导体','#ffb347'),('半导体材料设备','#ff5e3a'),('油气资源','#ff69b4'),
    ('商业航天','#ce93d8'),('人工智能','#ef9a9a'),
    ('云计算','#00e676'),('军工','#00c853'),('消费电子','#69f0ae'),
    ('CPO','#b9f6ca'),('通信','#a7ffeb'),('电力','#64ffda'),
    ('光伏','#1de9b6'),('国产算力','#00bfa5'),('AI应用','#009688'),
    ('有色金属','#00897b'),('医疗器械','#00796b'),('医疗服务','#004d40'),('医药生物','#00695c')
]
```

**纵坐标格式化 + 标签带方框 + 数值1位小数 + sign**：
```python
from matplotlib.ticker import FuncFormatter
def y_fmt(x, pos=None):
    return f'{int(x)}亿'
ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

# 按最新值降序排列（板块顺序固定）
latest = {n: dfs[n]['mainForce'].iloc[-1] for n,_ in sectors_info}
sorted_sectors = sorted(sectors_info, key=lambda x: latest[x[0]], reverse=True)

def update(frame):
    # ... setup axes ...
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
```

> 📌 标签格式：`存储芯片 +63.2`、`云计算 -5.1`（保留1位小数，方框颜色=曲线颜色，文字白色）
> 📌 纵坐标刻度显示 `50亿`、`0亿`、`-50亿`（FuncFormatter）

---

## 3. animation_player.py 已知 Bug（已修复）

| Bug | 症状 | 修复 |
|-----|------|------|
| 路径无扩展名 | `Unable to choose an output format` | line 197 添加 `if not save_path.endswith(('.mp4','.gif')): save_path += '.mp4'` |
| 无返回值 | `TypeError: unpack None` | line 216 添加 `return save_path` |

---

## 4. 竖屏参数速查

| 参数 | 值 |
|------|-----|
| 宽度×高度 | 1080×1920 |
| DPI | 120 |
| figsize | `(9, 16)` |
| fps | 8 |
| interval/帧 | 150ms |
| codec | libx264 |
| ffmpeg extra_args | `['-pix_fmt', 'yuv420p']` |

**陷阱**：必须 `plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']` 否则中文方块；`matplotlib.use('Agg')` 必须在 import pyplot 前设置。

---

## 5. 微信发送（阻塞点）

itchat/wxpy 在 headless cron 环境无法扫码登录，**所有方案均失败**。

唯一可行方向：提前在 GUI 终端手动 `wxpy` 登录并 `cache_path=True` 保存 `.pkl` 缓存，cron 任务复用缓存。Fisher 尚未完成此步骤，微信发送仍需手动。

---

## 6. 输出目录

- CSV：`/Users/mac/Downloads/Data/sector_data/`
- 视频：`/Users/mac/Downloads/主力资金数据/`
- 命名规范：`2026-05-18_{板块名}_主力资金动态.mp4`

---

> 📁 完整代码模板：见 `references/video-generation-code.md`