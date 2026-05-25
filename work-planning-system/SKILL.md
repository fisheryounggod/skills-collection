---
name: work-planning-system
description: 自动抓取飞书 Bitable + 市场数据，生成每日工作规划文档
triggers:
  - "工作规划"
  - "每日目标"
  - "飞书任务"
  - "定时任务"
---

# Work Planning System (工作规划系统)

## 系统概述
自动抓取飞书数据 + 市场信息，生成每日工作规划文档。

## 脚本位置
- 主脚本：`/home/yxf/scripts/work-planning-v2.py`
- 输出目录：`/home/yxf/workspace/daily-planning/`

## 数据源

| 数据源 | API | OAuth 需求 |
|--------|-----|-----------|
| 飞书文献清单 | Bitable API v2 (tenant token) | ❌ 无需用户授权 |
| 今日市场 | yfinance + 东方财富 | ❌ 无需 OAuth |

## 飞书 Bitable 配置
- **app_id**: `cli_a92714e0d2b8dbc4`
- **table_id**: `tblYu2fGXoYhxv1d`
- **base_id**: `bsetnNW9y5hVg2sA`
- **文献表字段**: 标题(title)、状态(status)、研究者(researcher)、优先级(priority)、预计时长(estimated_hours)、截止日期(due_date)

## 核心逻辑
1. 读取 Bitable 文献表，按状态过滤（进行中/待开始）
2. 抓取市场数据（S&P 500、A股）
3. AI 推荐今日核心目标（优先 高优先级 + 截止日期临近）
4. 生成时间块（上午/下午/晚上，6个块）

## Cronjob
```cron
0 9 * * * /usr/bin/python3 /home/yxf/scripts/work-planning-v2.py >> /home/yxf/workspace/logs/work-planning.log 2>&1
```

## OAuth 持久化说明（重要）
飞书 Task API 强制要求 user OAuth，refresh_token 30天过期，不适合自动化。
**推荐方案**：Bitable API (tenant token)，永久有效。

## 已知问题
- 飞书 OAuth refresh_token 已过期（2026-04-24）
- Task API 暂不可用，使用 Bitable 作为替代
