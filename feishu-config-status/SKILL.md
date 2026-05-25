---
type: skill
created: 2026-03-25
tags: [技能, 飞书, 配置]
---

# 飞书技能配置报告

> 飞书技能的配置状态与使用指南

---

## 🔍 配置现状

### OpenClaw配置文件
**位置**：`~/.openclaw/openclaw.json`

**当前状态**：❌ **飞书配置未加载**

**已加载的认证**：
```json
{
  "qwen-portal:default": {
    "provider": "qwen-portal",
    "mode": "oauth"
  },
  "zai:default": {
    "provider": "zai",
    "mode": "api_key"
  }
}
```

### 飞书技能目录
**位置**：`~/.openclaw/workspace/skills/`

**现有技能**：
```
skills/
├── feishu-create-doc/     # 飞书文档创建
└── feishu-note-organizer.js  # 飞书笔记组织（JS脚本）
```

---

## 🔑 飞书认证信息

### App ID与App Secret

**从历史记录获取的配置**：
```json
{
  "appId": "cli_a910623283f8dbcb",
  "appSecret": "NrfCFU9KoXNBLx7xbVq2xdr5cIAbsYXL"
}
```

**配置状态**：⚠️ **未加载到openclaw.json**

---

## 📋 需要执行的配置

### 配置飞书认证到openclaw.json

需要在`openclaw.json`中添加飞书认证：

```json
{
  "auth": {
    "profiles": {
      "feishu:default": {
        "provider": "feishu",
        "mode": "api_key",
        "app_id": "cli_a910623283f8dbcb",
        "app_secret": "NrfCFU9KoXNBLx7xbVq2xdr5cIAbsYXL"
      }
    }
  }
}
```

---

## 🛠️ 飞书技能详情

### 1. feishu-create-doc
**位置**：`skills/feishu-create-doc/`

**功能**：创建飞书云文档

**使用方式**：通过agent调用该技能

### 2. feishu-note-organizer.js
**位置**：`skills/feishu-note-organizer/`

**文件类型**：JavaScript脚本

**功能**：组织飞书笔记

**配置要求**：需要飞书App ID和App Secret

---

## 🚀 配置建议

### 立即行动

1. **添加飞书认证到openclaw.json**
   ```json
   {
     "auth": {
       "profiles": {
         "feishu:default": {
           "provider": "feishu",
           "mode": "api_key",
           "app_id": "cli_a910623283f8dbcb",
           "app_secret": "NrfCFU9KoXNBLx7xbVq2xdr5cIAbsYXL"
         }
       }
     }
   }
   ```

2. **验证配置**
   - 尝试调用飞书技能
   - 检查是否成功连接到飞书API

3. **测试常用功能**
   - 创建文档
   - 发送到指定群聊
   - 操作多维表格

---

## 📊 技能使用统计

### 常用飞书技能

| 技能名称 | 用途 | 使用频率 |
|---------|------|----------|
| feishu-create-doc | 创建文档 | 高 |
| feishu-bitable | 多维表格操作 | 高 |
| feishu-fetch-doc | 获取文档内容 | 中 |
| feishu-search-doc-wiki | 搜索知识库 | 中 |

---

## 🔧 故障排查

### 问题：飞书技能无法使用

**可能原因**：
1. ❌ 飞书认证未配置
2. ❌ App ID或App Secret错误
3. ❌ 飞书API服务异常

**解决步骤**：
1. 检查`openclaw.json`中是否包含飞书认证
2. 验证App ID和App Secret是否正确
3. 测试飞书API连接

### 问题：认证信息过时

**可能原因**：
- App Secret已过期
- App权限被撤销

**解决步骤**：
1. 在飞书开放平台重新生成App Secret
2. 更新`openclaw.json`中的配置
3. 重启OpenClaw Gateway

---

## 📝 相关文档

### 技能文档
- `skills/feishu-create-doc/SKILL.md` - 文档创建技能说明

### 配置文档
- `~/.openclaw/openclaw.json` - 主配置文件
- `~/.openclaw/agents/main/agent/config.json` - 主Agent配置

---

## 🎯 下一步行动

### 优先级P0
- [ ] 添加飞书认证到openclaw.json
- [ ] 验证飞书技能功能

### 优先级P1
- [ ] 测试常用飞书技能
- [ ] 建立飞书技能使用规范

### 优先级P2
- [ ] 创建飞书技能使用文档
- [ ] 建立飞书技能故障排查流程

---

## 📚 飞书技能参考

### 官方文档
- 飞书开放平台：https://open.feishu.cn/
- 飞书API文档：https://open.feishu.cn/document/

### 应用场景
- 创建文档记录笔记
- 发送报告到指定群聊
- 操作多维表格管理数据
- 搜索知识库查找内容

---

**配置状态**：⚠️ 飞书认证未加载到openclaw.json

**建议**：立即添加飞书认证以启用飞书技能功能。

---

*报告生成时间：2026-03-25 12:00*
