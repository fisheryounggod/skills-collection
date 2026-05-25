---
name: page-agent
description: |
  阿里巴巴开源的PageAgent：基于JavaScript的网页内GUI agent。
  用自然语言控制web界面，不需要浏览器扩展或headless browser。
  作为OpenClaw Skill包装，提供简单的API来调用PageAgent。
version: "1.0.0"
---

# PageAgent - 网页内GUI Agent

阿里巴巴开源的轻量级网页自动化方案，用自然语言控制web界面。

## 核心特性

- **基于JavaScript** - 一切在网页中发生，无需浏览器扩展
- **文本驱动** - 不需要截图、多模态LLM
- **自带LLM** - 可以用自己的模型
- **人在回路** - 漂亮的UI，用户可以看到每一步
- **零门槛** - 一行代码集成

## 应用场景

- **SaaS AI Copilot** - 产品内嵌AI助手，无需后端重写
- **Smart Form Filling** - 将20次点击工作流变成一句话
- **Accessibility** - 自然语言、语音命令、屏幕阅读器，零门槛
- **多页面Agent** - 可选Chrome扩展实现跨标签页协作

## OpenClaw Skill包装

PageAgent作为OpenClaw Skill提供简化的API调用。

### 安装PageAgent

```bash
# 方式1：CDN引入（快速试用）
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.5.8/dist/iife/page-agent.demo.js" crossorigin="true"></script>

# 方式2：npm安装（生产环境）
npm install page-agent

# 方式3：国内镜像
npm install page-agent --registry=https://registry.npmmirror.com
```

### 基础用法

```javascript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: 'YOUR_API_KEY',
  language: 'zh-CN'
})

await agent.execute('点击登录按钮')
```

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|---------|------|
| `model` | string | 'qwen3.5-plus' | 模型名称 |
| `baseURL` | string | - | API base URL |
| `apiKey` | string | - | API密钥 |
| `language` | string | 'en-US' | 语言 |
| `debug` | boolean | false | 调试模式 |

### 支持的模型

| 模型 | Provider | 说明 |
|------|----------|------|
| qwen3.5-plus | 阿里云通义千问 | 推荐 |
| qwen3.5-turbo | 阿里云通义千问 | 快速响应 |
| 自定义模型 | 任何OpenAI兼容API | 需配置baseURL和apiKey |

## OpenClaw集成

### 方式1：直接在HTML中使用

```html
<!DOCTYPE html>
<html>
<head>
  <title>PageAgent Demo</title>
  <script src="https://cdn.jsdelivr.net/npm/page-agent@1.5.8/dist/iife/page-agent.demo.js" crossorigin="true"></script>
</head>
<body>
  <button onclick="window.pageAgent.execute('点击登录按钮')">登录</button>
  <button onclick="window.pageAgent.execute('填写表单')">填写表单</button>
</body>
</html>
</html>
```

### 方式2：通过browser tool注入

```javascript
// 在网页中注入PageAgent脚本
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/page-agent@1.5.8/dist/iife/page-agent.demo.js';
script.crossOrigin = 'anonymous';
document.head.appendChild(script);

// 等待加载完成后执行
script.onload = () => {
  window.pageAgent.execute('执行某个操作');
};
```

### 方式3：创建自动化工作流

```javascript
// 定义工作流
const workflow = async () => {
  await window.pageAgent.execute('点击登录按钮');
  await window.pageAgent.execute('输入用户名：admin');
  await window.pageAgent.execute('输入密码：password123');
  await window.pageAgent.execute('点击提交按钮');
};

// 执行工作流
workflow();
```

## 常见任务示例

### 表单填写

```javascript
// 单个字段
await pageAgent.execute('在用户名输入框填入：admin');

// 批量填写
await pageAgent.execute(`
填写表单：
- 用户名：admin
- 邮箱：admin@example.com
- 密码：password123
`);
```

### 按钮点击

```javascript
// 简单点击
await pageAgent.execute('点击登录按钮');

// 按文本内容查找并点击
await pageAgent.execute('点击"提交"按钮');
```

### 导航操作

```javascript
// 链接导航
await pageAgent.execute('点击导航栏中的"产品"链接');

// 下拉菜单
await pageAgent.execute('点击"设置"下拉菜单');
```

### 数据提取

```javascript
// 提取文本
const text = await pageAgent.execute('提取页面上所有链接的文本');

// 提取结构化数据
const data = await pageAgent.execute('提取表格中的所有行数据');
```

## 高级功能

### 错误处理

```javascript
try {
  await agent.execute('执行某个操作');
} catch (error) {
  console.error('操作失败:', error);
  // 重试或回退逻辑
}
```

### 超时控制

```javascript
await agent.execute('点击登录按钮', { timeout: 5000 });
```

### 并行执行

```javascript
// 多个独立操作并行执行
await Promise.all([
  agent.execute('点击导航'),
  agent.execute('加载用户信息'),
  agent.execute('刷新数据')
]);
```

## 限制与注意事项

### 当前限制

- 仅支持JavaScript环境
- 需要页面支持DOM操作
- 复杂的iframe/Shadow DOM支持有限

### 注意事项

- API密钥安全性：不要在客户端代码中硬编码
- 权限控制：确保页面有足够的DOM操作权限
- 错误处理：网络、API、DOM操作都可能失败

## 与browser tool的区别

| 特性 | PageAgent | browser tool |
|------|-----------|--------------|
| 启动方式 | 网页内JavaScript | 独立浏览器进程 |
| 资源占用 | 极低（共享页面） | 高（独立进程） |
| 视觉反馈 | 用户可见每一步 | 难以实时反馈 |
| 跨页面 | 需Chrome扩展 | 原生支持 |
| 适用场景 | SaaS产品嵌入、表单自动化 | 通用爬虫、多页面任务 |

## 调试技巧

### 启用调试模式

```javascript
const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: 'YOUR_API_KEY',
  debug: true  // 启用调试输出
});
```

### 查看执行日志

```javascript
// 在浏览器控制台查看详细日志
console.log('PageAgent执行日志:', window.pageAgent.getLogs());
```

### DOM探索

```javascript
// 手动探索DOM结构
document.querySelector('#login-button').innerHTML
document.querySelectorAll('input[type="text"]')
```

## 相关资源

- **GitHub**: https://github.com/alibaba/page-agent
- **Demo**: https://alibaba.github.io/page-agent/
- **Docs**: https://alibaba.github.io/page-agent/docs/introduction/overview
- **HN讨论**: https://news.ycombinator.com/item?id=47256381
- **依赖项目**: browser-use (MIT License)

## 免费API（测试用）

PageAgent CDN提供的免费测试API用于技术评估：
- 地址：https://alibaba.github.io/page-agent/docs/features/models#free-testing-api
- 限制：仅用于技术评估
- 同意条款：使用即表示同意其[terms](https://github.com/alibaba/page-agent/blob/main/docs/terms-and-privacy.md)

---

*基于page-agent v1.5.8*
