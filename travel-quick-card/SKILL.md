---
name: travel-quick-card
description: 轻量出行卡片生成 — 接收目的地+偏好，自动生成结构化信息卡片 PNG 并可投递至 Telegram。用户说「出行计划」「美食攻略」「打卡清单」「几天去哪」，且内容较简单（无需深度研究）时触发。
version: 1.0
---

# Travel Quick Card

轻量出行卡片生成 — Destination + Preferences → PNG Card → 可选投递 Telegram。

## 触发条件

用户说「出行计划」「美食攻略」「打卡清单」「X天X夜」「去哪里好玩」，且：
- 目的地明确（城市名）
- 偏好简单（情侣/亲子/独自/朋友，预算档位，打卡/美食/休闲）
- 无需深度历史文化研究

**不适用**：需考古研究、博物馆攻略、古建深度功课 → 用 `ljg-travel` 代替。

## 参数

| 参数 | 说明 |
|------|------|
| `-t` | 卡片类型：`itinerary`（行程）/ `food`（美食）/ `spots`（打卡清单）/ `mixed`（综合） |
| `-d` | 目的地，省略时从上下文推断 |
| `-p` | 偏好组合：`couple`（情侣）/ `family`（亲子）/ `friends`（朋友）/ `solo`（独自）/ `business`（商务） |
| `-b` | 预算：`budget`（穷游）/ `comfort`（舒适）/ `luxury`（奢侈） |
| `--send` | 生成后自动发送到 Telegram |

## 执行

### 1. 收集信息

从对话中提取（无需主动询问，除非缺少关键信息）：
- 目的地
- 天数
- 人员构成（情侣/朋友/家庭）
- 偏好类型（打卡/美食/休闲/亲子）
- 预算档位

如缺少非关键信息，用最常见假设补全，直接生成不卡流程。

### 2. 生成卡片 HTML

模板风格选择：
- **行程/itinerary**：米白底 + 粉色系，清晰三段式布局
- **美食/food**：暗黑底 + 琥珀色/橙色，现代感
- **打卡/spots**：白底 + 绿色系，网格卡片
- **综合/mixed**：混合布局

卡片必须包含：
- 目的地 + 主题标签
- 具体地点名称（不是泛泛描述）
- 时间段/地点属性
- 实用Tips（2-4条）

HTML 模板保存到 `/tmp/{name}.html`

### 3. 截图生成 PNG

```bash
cd /path/to/ljg-card/assets
node capture.js <html_path> <output_png> 1080 <height> fullpage
```

`ljg-card` assets 路径：`/Users/mac/.hermes/skills/ljg-card/assets/`

如 Playwright 未安装：
```bash
cd /path/to/ljg-card/assets && npm install playwright && npx playwright install chromium
```

PNG 输出路径：`~/hermes/travel/{name}.png`

### 4. 投递 Telegram（如指定 `--send`）

```python
send_message(message="卡片名称已生成 📸", target="telegram:<chat_id>")
send_message(message="MEDIA:/path/to/card.png", target="telegram:<chat_id>")
```

默认 chat_id：`871499404`

### 5. 汇总

```
{name}.png 已生成
保存路径：~/hermes/travel/{name}.png
```

## 约束

- 地点信息必须是真实可查的，不编造餐厅/景点名
- 单张卡片信息量适中，不堆砌
- 生成时参考已有文件：`~/hermes/travel/` 下有历史卡片可参考风格
- HTML 内联 CSS，禁止外部依赖（字体除外）
