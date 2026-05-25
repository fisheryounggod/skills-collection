---
name: overseas-ecommerce-english-plan
description: |
  海外电商直播英语口语强化学习计划生成。触发词：「直播英语」「电商英语」「海外电商」「英语学习计划」「30天计划」「直播带货英语」
  基于 TikTok Shop / Amazon Live / Whatnot 等平台实战需求。
created: 2026-04-23
tags: [英语学习, 电商直播, 口语, 海外电商, TikTok Shop, 直播带货]
---

# 海外电商直播英语 · 30天强化学习计划

目标：能在海外电商平台（TikTok Shop / Amazon Live / Whatnot / 独立站直播）进行英语直播带货。

## 计划结构（4周）

### Week 1：词汇筑基 + 基础话术
**核心能力**：直播开场、自我介绍、FAB产品介绍、价格话术、催单、收尾

**每日交付**：朗读录音 → 发微信

| 天 | 主题 | 核心词汇 | 实战任务 |
|----|------|---------|---------|
| Day 1 | 直播开场与迎新 | live stream, welcome, going live, join us, hit follow | 5个黄金开场白各3遍 |
| Day 2 | 自我介绍 | host, presenter, ambassador, passionate about, specialize in | 自我介绍模板3遍 |
| Day 3 | FAB产品介绍 | feature, benefit, advantage, value, suit for | FAB模板5个产品 |
| Day 4 | 价格话术 | starts at, only, exclusive, limited, discount, off | 价格介绍5场景 |
| Day 5 | 催单话术 | don't miss, last chance, selling fast, 3-2-1, almost gone | 催单话术10句 |
| Day 6 | 收尾与关注引导 | follow, like, subscribe, see you next time, don't miss | 收尾话术模板 |
| Day 7 | 本周复习 | 综合所有句型 | 3分钟连续自我介绍+产品介绍 |

### Week 2：产品话术 + 促销心理
**核心能力**：Q&A应答、产品展示、竞品对比、优惠码、促销、捆绑套餐

**新增交付**：Q&A场景问答录音

| 天 | 主题 | 核心词汇 | 实战任务 |
|----|------|---------|---------|
| Day 8 | 观众Q&A应对 | sure, absolutely, great question, let me explain, here's the thing | 6大Q&A问题应答 |
| Day 9 | 产品展示话术 | look at this, check this out, notice how, here we have, take a look | 产品展示描述 |
| Day 10 | 竞品对比话术 | compared to, unlike, the difference is, what sets us apart | 对比话术3场景 |
| Day 11 | 优惠码与促销 | use code, apply at checkout, promo, deal, bundle, save $X | 促销话术5句 |
| Day 12 | 退货政策话术 | 30-day, hassle-free, money-back, guarantee, return | 退货政策应答 |
| Day 13 | 捆绑套餐话术 | bundle, package, combo, set, deal, more bang for buck | 套餐话术3句 |
| Day 14 | 本周复习 | 综合所有句型 | Q&A+价格+促销场景演练 |

### Week 3：互动实战 + 异议处理
**核心能力**：处理价格异议、质量疑虑、观众互动、节日促销、说服心理

**新增交付**：即兴应变录音

| 天 | 主题 | 核心词汇 | 实战任务 |
|----|------|---------|---------|
| Day 15 | 价格异议处理 | worth every penny, investment, quality speaks, you get what you pay | 价格异议5答 |
| Day 16 | 质量疑虑应对 | premium, certified, authentic, warranty, durable, material | 质量保证应答 |
| Day 17 | 观众互动留人 | comment, let us know, type in chat, we see you, welcome | 互动话术+留人 |
| Day 18 | 节日促销特辑 | holiday special, limited time, gift for someone, stocking stuffer | 节日促销开场 |
| Day 19 | 说服心理学 | urgency, scarcity, social proof, authority, reciprocity | 心理话术应用 |
| Day 20 | 即兴应变训练 | 随机产品/随机刁难问题 | 即兴发挥2分钟 |
| Day 21 | 本周复习 | 综合所有句型 | 全流程无稿演练 |

### Week 4：综合演练 + 模拟直播
**核心能力**：全流程整合、薄弱环节突破、完整模拟直播

**新增交付**：15分钟完整直播模拟录音

| 天 | 主题 | 核心词汇 | 实战任务 |
|----|------|---------|---------|
| Day 22 | 全流程彩排 | 完整直播6步骤 | 逐字稿 → 脱稿 → 即兴 |
| Day 23 | 薄弱环节突破 | 弱点话题强化 | 针对弱项重复练习 |
| Day 24 | 15分钟完整模拟 | 全流程 | 完整直播+录屏复盘 |
| Day 25 | 即兴发挥特训 | 随机产品 | 3次即兴发挥各5分钟 |
| Day 26 | 复杂Q&A应对 | 刁难问题 | 5个最难Q&A专项训练 |
| Day 27 | 完整模拟直播 | 真实直播感 | 15分钟直播+录屏复盘 |
| Day 28 | 语速与节奏 | pacing, slow down, enunciate | 录音自检语速 |
| Day 29 | 毕业设计 | 完整直播 | 20分钟完整直播+录屏 |
| Day 30 | 总结+未来计划 | 学习成果 | 录音总结+下一步 |

## 每日 Cron 提醒

创建每日09:00自动提醒脚本：

```bash
#!/bin/bash
source /home/yxf/.bashrc
conda activate hermes-agent

START_DATE="2026-04-24"
TODAY=$(date +%Y-%m-%d)
DAY_NUM=$((($(date -d "$TODAY" +%s) - $(date -d "$START_DATE" +%s)) / 86400 + 1))
WEEK_NUM=$(((DAY_NUM - 1) / 7 + 1))
DAY_IN_WEEK=$(((DAY_NUM - 1) % 7 + 1))

bash /home/yxf/scripts/english-learning-reminder.sh
```

## 核心学习原则

1. **场景驱动**：每个词汇/句型都绑定具体直播场景，不用孤立记忆
2. **实战为主**：每天必须有录音交付，从 Day 8 起加入即兴应变
3. **循序渐进**：Week 1 跟读 → Week 2 独立应答 → Week 3 即兴 → Week 4 完整直播
4. **量化交付**：每天录音发微信，第24/27/29天录屏复盘

## 参考资源

- TikTok Shop 英文直播话术研究
- Amazon Live 主播脚本模板
- Whatnot 拍卖英语话术
- Kua.ai 跨境电商内容工具
