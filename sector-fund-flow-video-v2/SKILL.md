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

> ⚠️ **Cron deliver 必须是显式微信 ID**：使用 `weixin:o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat`，不能用 `"origin"`。background session 中 origin 解析失败，视频不会推送。
>
> ⚠️ **标题不要用 emoji**：Microsoft YaHei 字体不支持 ⚡🌾 等 emoji，会显示为方块。标题用中文括号如 `【新能源】主力资金分时流向`。

## 路径速查

> 📋 **板块 secid 速查表**：`references/sector-secids.md`（农业12板块、新能源12板块、更多有效/无效板块列表）

- CSV数据：`/Users/mac/Downloads/Data/sector_data/`
- 视频输出：`/Users/mac/Downloads/主力资金数据/`
- 动画引擎：`/Users/mac/Downloads/Data/animation_player.py`
- API状态：`references/eastmoney-api-status.md`
- 板块 secid 参考：`references/sector-secids.md`

> ⚠️ **API 端点选择**：`push2.eastmoney.com` 在部分网络环境（Hertz/BigAI farm）间歇性断开，**必须用 `push2delay.eastmoney.com`** 替代。`www.eastmoney.com` 主站通常正常。如遇 `RemoteDisconnected: HTTP 000`，切换到 delay 端点即可。

> ⚠️ **关键 bug**：东方财富 API 返回的 mainForce 是原始值（如 63亿+ = 6321804626），CSV 保存的是原始值，**读取时必须除以 1e8 转换为"亿"**，否则视频标签数字显示为亿级。

> ⚠️ **Cron deliver 必须是显式微信 ID**：使用 `weixin:o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat`，不能用 `"origin"`。background session 中 origin 解析失败，视频不会推送。

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
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

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
today = datetime.now().strftime('%Y-%m-%d')

# 读取时统一除以 1e8 转为"亿"
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
    # 15:00 收盘金色虚线（固定在15:00位置或数据终点，标签显示数据实际截止时间）
    target_idx = next((i for i,t in enumerate(times) if '15:00' in t), N-1)
    label_time = times[target_idx].split(' ')[1] if ' ' in times[target_idx] else times[target_idx]
    ax.axvline(x=target_idx, color='#FFD700', linewidth=1.2, linestyle='--', alpha=0.7)
    ax.text(target_idx, y_max + y_margin * 0.3, label_time, color='#FFD700', fontsize=9,
            ha='center', va='bottom', fontweight='bold')

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

    ax.text(0.5, -0.06, f'数据区间 09:31 ~ 15:00', transform=ax.transAxes, color='#888', fontsize=9, ha='center')

# 三倍速：interval=67ms（原200ms/3），fps=15（原5*3）
ani = animation.FuncAnimation(fig, update, frames=N, blit=False, interval=67)
save_path = f'{OUTPUT}{today}_主力资金分时对比_label.mp4'
ani.save(save_path, writer='ffmpeg', fps=15, dpi=DPI, codec='libx264', extra_args=['-pix_fmt', 'yuv420p'])
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
| fps | 15（三倍速）/ 5（标准） |
| interval/帧 | 67ms（三倍速）/ 200ms（标准） |
| codec | libx264 |
| ffmpeg extra_args | `['-pix_fmt', 'yuv420p']` |

## 4. 微信发送（已验证可用）

hermes-agent 执行环境已内置 `WEIXIN_*` 环境变量（`WEIXIN_TOKEN`、`WEIXIN_ACCOUNT_ID`、`WEIXIN_BASE_URL`、`WEIXIN_CDN_BASE_URL`），直接调用 `send_message_tool` 即可，无需 openclaw 或 wxpy。

> ⚠️ **iLink session expiry（errcode=-14）处理**：WeChat iLink 会话超时后，gateway 会自动暂停 10 分钟，期间所有发送（包括重试）均返回 `session timeout`。症状：
> ```
> [Weixin] session expired for o9cq802n; retrying without context_token
> [Weixin] send chunk failed to=o9cq802n attempt=2/5 ... errcode=-14 errmsg=session timeout
> ...
> [Weixin] Session expired; pausing for 10 minutes
> ```
> **不要在此时窗口内反复重试**——gateway 本身已经进入保护性暂停，硬重试只会浪费调用配额。正确做法：
> 1. 立即记录失败，不做额外重试调用
> 2. 启动 background process：`sleep 660 && send_message ...`（等 11 分钟，留 1 分钟余量）
> 3. 等待 background 进程完成后验证发送结果
>
> 检查方法：`tail -5 ~/.hermes/logs/gateway.log | grep -i "pausing\|expired"` 有 `pausing for 10 minutes` 则确认是 session expiry。

### 4.1 单次生成（agent 直接执行）

```python
import sys
sys.path.insert(0, '/Users/mac/.local/bin/hermes-agent')
from tools.send_message_tool import send_message_tool

chat_id = 'o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat'
video_path = f'/Users/mac/Downloads/主力资金数据/{today}_主力资金分时对比_label.mp4'

result = send_message_tool({
    'action': 'send',
    'target': f'weixin:{chat_id}',
    'message': f'📈 主力资金板块分时流向对比  {today}',
    'media_files': [video_path]
})
```

### 4.2 Cron 定时任务（必须用 2-step 发送）

⚠️ **Cron agent 在 background session 中会偷懒——只发文字不发视频。必须拆成两步，每步单独调用 send_message：**

**第一步**：用 send_message 工具发送文字消息：
```
target: weixin:o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat
message: 📈 主力资金板块分时流向对比  {当天日期}
```

**第二步**：用 send_message 工具发送视频文件：
```
target: weixin:o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat
message: MEDIA:/Users/mac/Downloads/主力资金数据/{当天日期}_主力资金分时对比_label.mp4
```

**deliver 必须是显式 Weixin ID**，不能用 `"origin"`——background session 中 origin 解析失败，视频不会推送：
```
deliver: weixin:o9cq802nxSy8F1d7Vc65-XgAe83E@im.wechat
```

> ⚠️ 不要用 `asyncio.run()` 调用 `send_message_tool`——它是同步函数。
> ⚠️ 不要依赖 openclaw gateway——它在此环境中未运行，openclaw-weixin 账号文件不存在。
> ⚠️ 不要用 wxpy/itchat——headless cron 无法扫码登录。

## 5. 输出目录

- CSV：`/Users/mac/Downloads/Data/sector_data/`
- 视频：`/Users/mac/Downloads/主力资金数据/`
- 命名规范：`2026-05-18_主力资金分时对比_label.mp4`

## 6. v2 视觉标准（最终版）

- **22色全色轮**：红→橙→黄→绿→青→蓝→紫→粉，无重复色相
- **方框标签**：白色文字 + 颜色填充圆角矩形 `round,pad=0.3`
- **数字**：保留1位小数（如 `+63.2`）
- **标题**：`主力资金板块分时流向对比  {日期}`
- **15:00金色虚线**：`#FFD700`，linewidth=1.2，linestyle='--'，alpha=0.7
- **底部标注**：`数据区间 09:31 ~ 15:00`
- **纵坐标**：刻度显示整数+"亿"（如 `50亿`、`0亿`、`-50亿`）
- **三倍速**：interval=67ms，fps=15，播放时间约16秒（vs 标准200ms/5fps约48秒）