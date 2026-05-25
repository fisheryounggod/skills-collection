# Research Skill - Enhanced with Voice Explanation

## Overview

Conduct deep research using Gemini CLI and automatically provide voice explanation along with the report.

## Workflow

### 1. Spawn Research Agent
When user says "Research: [topic]", spawn sub-agent to research using Gemini CLI:

```
sessions_spawn(
  task: "Research: [FULL TOPIC WITH CONTEXT]
  
Use Gemini CLI to research this topic. Run:

gemini --yolo \"[RESEARCH PROMPT]\"

Research should cover:
1. Overview & Core Concepts - what is this, terminology, why it matters
2. Current State - latest developments, major players
3. Technical Deep Dive - how it works, mechanisms, key techniques
4. Practical Applications - real-world use cases, tools available
5. Challenges & Open Problems - technical, ethical, barriers
6. Future Outlook - trends, predictions, emerging areas
7. Resources - key papers, researchers, communities, courses

Save to: ~/clawd/research/[slug]/research.md

IMPORTANT - When research is complete:
1. Send a wake event immediately:
   cron(action: 'wake', text: '🔬 Research complete: [TOPIC]. Key findings: [3-4 bullet points]. Full report: ~/clawd/research/[slug]/research.md', mode: 'now')
2. When asked to produce an announce message, reply exactly: ANNOUNCE_SKIP",
  label: "research-[slug]")
```

### 2. Handle Wake Event
When wake event is received:
1. Send text summary with key findings
2. Generate voice explanation using tts() - summarize 3-5 key points
3. Send voice using openclaw message send

Voice script template:
"Research complete. Key findings: [Point 1], [Point 2], [Point 3]. Full report has been saved."

### 3. Voice Explanation Format

Voice explanation should include:
- Research topic name
- 3-5 key findings (most important points)
- Brief conclusion or recommendation

Example:
"Research complete: China A-share market decline. Key findings: First, economic slowdown with GDP dropping from 5.5% to 4.8%. Second, policy transmission inefficiencies. Third, capital outflow of 400 billion RMB. Full report saved to research folder."

## User Preferences

- **Research reports must include voice explanation**
- **Voice message sending workflow**: Use tts() + openclaw message send

## Configuration

- Research output directory: `~/clawd/research/`
- TTS default voice: zh-CN-XiaoxiaoNeural (Chinese female)
- Telegram target: @xiongfeel (ID: 871499404)

## Notes

- Gemini CLI is authenticated and ready for use
- Research typically takes 3-8 minutes
- Voice explanation is generated after research completes
- Voice explanation should be concise (3-5 points, 30-60 seconds)

## Examples

### Example 1: CBDC Research
```
Research: CBDC

Wake event received:
- Text: "CBDC research complete! Key findings: 134 countries exploring, China's e-CNY largest pilot with $982B transactions."
- Voice: tts("CBDC research complete. Key findings: First, 134 countries exploring CBDCs covering 98% of global GDP. Second, China's e-CNY is world's largest pilot with $982 billion cumulative transactions. Third, 19 of 20 G20 nations in advanced stages. Full report saved.")
```

### Example 2: A-Share Decline Research
```
Research: A股下跌原因

Wake event received:
- Text: "A-share decline research complete! Multi-factor downturn: economic slowdown, policy inefficiencies, capital flight."
- Voice: tts("A-share decline research complete. Key findings: First, economic slowdown with GDP dropping from 5.5% to 4.8%. Second, policy transmission inefficiencies. Third, capital outflow of 400 billion RMB. Fourth, market down 13.6% with retail investors prone to herd behavior. Full report saved.")
```
