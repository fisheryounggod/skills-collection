# sector-fund-flow-video-v2 执行指南

## 执行环境说明

### Python 环境选择（关键！）

| 工具 | Python | pandas可用 | 备注 |
|------|--------|------------|------|
| `terminal()` | venv python | ❌ 无pandas | hermes-agent 默认环境 |
| `execute_code()` | 独立 Python | ✅ `/usr/bin/python3` 有 | 用于数据拉取和视频生成 |

**两种执行方式的组合使用：**

```python
# 方式A（推荐）：全程用 execute_code + /usr/bin/python3
result = subprocess.run(['/usr/bin/python3', '-c', script], ...)
```

```python
# 方式B：terminal 用 curl 拉数据 + execute_code 生成视频
# 1. terminal: curl eastmoney API → 保存CSV
# 2. execute_code: 用 /usr/bin/python3 读CSV → matplotlib动画 → ffmpeg
```

### 为什么终端直接跑 python3 会超时？

`terminal()` 默认使用 `~/.hermes/hermes-agent/venv/bin/python`，该 venv 没有安装 pandas/matplotlib/numpy。

解决方案：**始终通过 `execute_code` 调用 `/usr/bin/python3`**（系统Python，已有完整数据科学栈）。

## Eastmoney API 关键发现

### 正确的 API 端点

```
https://push2delay.eastmoney.com/api/qt/stock/fflow/kline/get
```

- **不能用** `eastmoney_sector_flow.py`（secid 映射不全，化工/医疗数据永远是旧数据）
- **必须直接调 API**，参数见 SKILL.md

### 字段说明

kline 返回格式：`time, mainForce, small, medium, large, superLarge`
- `mainForce` = 主力资金净流入（原始单位，非"亿"，需除以 1e8）
- 时间格式：`2026-05-22 09:31` ~ `2026-05-22 15:00`（240个分时数据点）

### API 可用性验证

```bash
# 快速验证（不走 Python）
curl -s --max-time 10 "https://push2delay.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=1&secid=90.BK1137&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63" | head -c 200
```

## 视频生成脚本核心参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 分辨率 | 1080×1920 | 竖屏9:16 |
| DPI | 120 | |
| figsize | (9, 16) | inch |
| fps | 5 | |
| 帧间隔 | 200ms | |
| codec | libx264 | ffmpeg |
| ffmpeg extra | `['-pix_fmt', 'yuv420p']` | 兼容性 |

## 微信发送状态

- **当前状态**：iLink rate limit 拦截，发送失败
- **微信ID**：`o9cq802nxSy8F1d7Vc65-XgAe83E` 和 `o9cq801rqSFjl8od4ss5V3u01M2w` 均被限流
- **手动方案**：视频已保存在 `/Users/mac/Downloads/主力资金数据/`，需手动发送
- **自动方案**：见 SKILL.md 微信章节（依赖 .pkl 缓存，未完成配置）

## 已知数据（2026-05-22 收盘）

主力净流入 TOP3：CPO +103亿、大科技 +91亿、国产算力 +74亿
主力净流出：AI应用 -24亿、半导体材料设备 -8亿、医疗服务 -2亿
