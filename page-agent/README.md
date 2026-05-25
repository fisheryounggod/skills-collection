# PageAgent for OpenClaw

OpenClaw Skill包装，提供简化的PageAgent使用方式。

## 快速开始

### 1. 在HTML中使用PageAgent

```html
<!DOCTYPE html>
<html>
<head>
  <title>My App with PageAgent</title>
  <script src="https://cdn.jsdelivr.net/npm/page-agent@1.5.8/dist/iife/page-agent.demo.js" crossorigin="true"></script>
</head>
<body>
  <h1>PageAgent Demo</h1>
  <button onclick="demoAction()">执行操作</button>

  <script>
    async function demoAction() {
      try {
        await window.pageAgent.execute('点击登录按钮');
        console.log('操作完成');
      } catch (error) {
        console.error('操作失败:', error);
      }
    }
  </script>
</body>
</html>
```

### 2. 使用自定义模型

```javascript
const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: 'YOUR_API_KEY',
  language: 'zh-CN'
});
```

### 3. 创建自动化工作流

```javascript
const loginWorkflow = async () => {
  await agent.execute('找到登录按钮');
  await agent.execute('点击登录按钮');
  await agent.execute('输入用户名：admin');
  await agent.execute('输入密码：password123');
  await agent.execute('点击提交按钮');
};

loginWorkflow();
```

## 配置阿里云通义千问

### 获取API Key

1. 访问 https://dashscope.aliyuncs.com/
2. 注册/登录
3. 创建API Key
4. 记录API Key（sk-xxx格式）

### 配置PageAgent

```javascript
const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: 'sk-your-api-key-here',
  language: 'zh-CN'
});
```

## 使用示例

### 示例1：表单自动填写

```javascript
// 单个字段填写
await agent.execute('在姓名输入框填入：张三');

// 批量填写
await agent.execute(`
填写个人信息表单：
- 姓名：张三
- 邮箱：zhangsan@example.com
- 电话：13800138000
- 地址：北京市朝阳区
`);
```

### 示例2：智能导航

```javascript
// 按内容查找并点击
await agent.execute('找到并点击"产品"链接');

// 下拉菜单操作
await agent.execute('打开"设置"下拉菜单');
await agent.execute('选择"账户设置"');
```

### 示例3：数据提取

```javascript
// 提取表格数据
const tableData = await agent.execute('提取页面上的表格数据');

// 提取链接列表
const links = await agent.execute('提取页面上所有链接的URL和标题');
```

## 实际应用场景

### 场景1：SaaS产品AI Copilot

```html
<!-- 在你的产品页面中集成 -->
<script src="https://cdn.jsdelivr.net/npm/page-agent@1.5.8/dist/iife/page-agent.demo.js"></script>

<button onclick="copilotAction()">
  AI Copilot
</button>

<script>
  async function copilotAction() {
    // 用户可以输入自然语言命令
    const command = prompt('请输入命令：');
    if (command) {
      await window.pageAgent.execute(command);
    }
  }
</script>
```

### 场景2：ERP系统表单填写

```javascript
// 复杂表单的一键填写
const fillERPForm = async (data) => {
  await agent.execute(`
填写ERP表单：
- 供应商名称：${data.supplier}
- 采购单号：${data.orderNo}
- 物品名称：${data.product}
- 数量：${data.quantity}
- 单价：${data.price}
- 备注：${data.remark}
  `);
};

fillERPForm({
  supplier: '供应商A',
  orderNo: 'PO20260318001',
  product: '商品X',
  quantity: '100',
  price: '50.00',
  remark: '紧急采购'
});
```

### 场景3：数据录入辅助

```javascript
// 从结构化数据自动填写
const fillForm = async (formData) => {
  for (const [field, value] of Object.entries(formData)) {
    await agent.execute(`在"${field}"字段填入：${value}`);
  }
};

fillForm({
  '用户名': 'admin',
  '邮箱': 'admin@example.com',
  '部门': '技术部'
});
```

## 调试与错误处理

### 启用详细日志

```javascript
const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: 'YOUR_API_KEY',
  debug: true  // 启用详细日志
});

// 查看执行日志
const logs = agent.getLogs();
console.table(logs);
```

### 错误处理模式

```javascript
async function safeExecute(command, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const result = await agent.execute(command);
      return result;
    } catch (error) {
      console.error(`尝试${i + 1}失败:`, error);
      if (i === retries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

// 使用
safeExecute('点击登录按钮', 3);
```

## 最佳实践

### 1. 使用明确的命令

```javascript
// 好
await agent.execute('点击登录按钮');

// 避免
await agent.execute('登录');  // 太模糊
```

### 2. 批量操作时使用自然语言描述

```javascript
// 好
await agent.execute(`
填写表单：
- 用户名：admin
- 密码：123456
`);

// 避免
await agent.execute('填写用户名');
await agent.execute('填写密码');  // 多次调用
```

### 3. 处理异步操作

```javascript
// 等待页面加载
await agent.execute('等待页面加载完成');
await agent.execute('点击登录按钮');

// 等待元素出现
await agent.execute('等待登录按钮出现');
await agent.execute('点击登录按钮');
```

### 4. 使用容错机制

```javascript
async function robustOperation() {
  try {
    await agent.execute('点击按钮');
  } catch (error) {
    console.error('操作失败，尝试备用方案');
    await agent.execute('使用键盘快捷键回车');
  }
}
```

## 性能优化

### 1. 减少API调用

```javascript
// 合并多个操作
await agent.execute('同时点击导航和加载数据');

// 避免重复操作
if (!visited) {
  await agent.execute('访问页面');
  visited = true;
}
```

### 2. 使用缓存

```javascript
const cache = new Map();

async function cachedExecute(command) {
  if (cache.has(command)) {
    return cache.get(command);
  }
  
  const result = await agent.execute(command);
  cache.set(command, result);
  return result;
}
```

### 3. 批量处理

```javascript
const tasks = [
  '填写表单A',
  '填写表单B',
  '填写表单C'
];

await Promise.all(tasks.map(task => agent.execute(task)));
```

## 常见问题

### Q1: PageAgent找不到页面元素

**原因**: 元素选择器不准确或页面动态加载

**解决**:
```javascript
// 等待元素出现
await agent.execute('等待元素加载完成');
await agent.execute('点击特定按钮');
```

### Q2: API调用失败

**原因**: API Key无效或网络问题

**解决**:
```javascript
// 检查API Key
console.log('API Key状态:', agent.checkAPIKey());

// 使用重试机制
await safeExecute('某个操作', 3);
```

### Q3: 执行超时

**原因**: 操作太复杂或网络慢

**解决**:
```javascript
// 增加超时时间
await agent.execute('复杂操作', { timeout: 30000 });
```

## 与其他工具的对比

| 工具 | 启动方式 | 资源占用 | 视觉反馈 | 适用场景 |
|------|---------|---------|---------|---------|
| PageAgent | 网页内JavaScript | 极低 | 用户可见 | SaaS产品嵌入、表单自动化 |
| browser tool | 独立浏览器 | 高 | 难以反馈 | 通用爬虫、多页面任务 |
| Playwright | 独立浏览器 | 高 | 截图/录像 | 自动化测试、爬虫 |

## 更新日志

### v1.0.0 (2026-03-18)

- 初始版本
- 支持基本的PageAgent包装
- 提供OpenClaw集成示例
- 添加常见应用场景

## 相关链接

- [PageAgent GitHub](https://github.com/alibaba/page-agent)
- [PageAgent Demo](https://alibaba.github.io/page-agent/)
- [PageAgent Docs](https://alibaba.github.io/page-agent/docs/introduction/overview)
- [OpenClaw Skills](https://clawhub.com/skills)

## 许可证

PageAgent 基于 browser-use 项目（MIT License）构建。

---

*最后更新: 2026-03-18*
