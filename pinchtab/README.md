# PinchTab Skill for OpenClaw

PinchTab 是一个强大的浏览器控制工具，为 AI agent、脚本和自动化工作流提供浏览器控制能力。

## 快速开始

### 1. 安装 PinchTab

运行设置脚本：

```bash
bash skills/pinchtab/scripts/setup.sh
```

或手动安装：

```bash
# 一键安装（推荐）
curl -fsSL https://pinchtab.com/install.sh | bash

# 或使用 npm
npm install -g pinchtab

# 或使用 Docker
docker run -d -p 9867:9867 pinchtab/pinchtab
```

### 2. 验证安装

```bash
pinchtab --version
```

### 3. 启动服务器

```bash
pinchtab
```

服务器会运行在 `http://127.0.0.1:9867`

### 4. 启动浏览器实例

```bash
pinchtab instance start
```

### 5. 导航到页面

```bash
pinchtab nav https://example.com
```

## 基本使用

### 检查页面

```bash
# 获取交互式元素（推荐）
pinchtab snap -i -c
```

返回示例：
```json
{
  "nodes": [
    { "ref": "e0", "role": "link", "name": "Home" },
    { "ref": "e1", "role": "button", "name": "Submit" },
    { "ref": "e2", "role": "textbox", "name": "Email" }
  ]
}
```

### 点击元素

```bash
pinchtab click e1
```

### 输入文本

```bash
pinchtab type e2 "test@example.com"
```

### 截图

```bash
pinchtab screenshot /tmp/screenshot.png
```

## Python API

```python
from skills.pinchtab.scripts.pinchtab import PinchTab

# 创建浏览器实例
browser = PinchTab()

# 导航
browser.nav("https://example.com")

# 获取页面快照
snapshot = browser.snap(interactive=True, compact=True)
print(f"Found {len(snapshot['nodes'])} elements")

# 点击元素
if snapshot['nodes']:
    first_ref = snapshot['nodes'][0]['ref']
    browser.click(first_ref)

# 输入文本
browser.type("e0", "Hello, World!")

# 截图
browser.screenshot("/tmp/screenshot.png")
```

## 常见场景

### 自动化表单填写

```bash
# 1. 打开表单
pinchtab nav https://example.com/form

# 2. 获取快照
pinchtab snap -i -c > snapshot.json

# 3. 填写表单
pinchtab type e0 "John Doe"
pinchtab type e1 "john@example.com"
pinchtab type e2 "password123"

# 4. 提交
pinchtab click e3
```

### 网页数据抓取

```python
import json
from skills.pinchtab.scripts.pinchtab import PinchTab

browser = PinchTab()
browser.nav("https://example.com")

# 获取页面文本
text_data = browser.text()
print(text_data)

# 获取结构化数据
snapshot = browser.snap(interactive=True, compact=True)
for node in snapshot['nodes']:
    print(f"{node['role']}: {node['name']}")
```

### 页面测试

```bash
# 导航到测试页面
pinchtab nav https://example.com

# 截图对比
pinchtab screenshot /tmp/before.png

# 执行操作
pinchtab click e0

# 截图验证
pinchtab screenshot /tmp/after.png
```

## 更多命令

### 导航操作

```bash
pinchtab nav <url>         # 导航到 URL
pinchtab reload              # 刷新页面
pinchtab back                # 后退
pinchtab forward             # 前进
```

### 元素交互

```bash
pinchtab click <ref>         # 点击元素
pinchtab type <ref> <text>  # 输入文本
pinchtab fill <ref> <value>  # 填充表单
pinchtab press <key>         # 按键（Enter, Escape 等）
pinchtab hover <ref>         # 悬停
pinchtab focus <ref>         # 聚焦
pinchtab select <ref>        # 选择
pinchtab scroll <direction>  # 滚动（up, down, top, bottom）
```

### 输出

```bash
pinchtab screenshot <path>    # 截图
pinchtab pdf <path>         # 导出 PDF
pinchtab text               # 获取页面文本
```

### 高级

```bash
pinchtab eval "document.title"         # 执行 JavaScript
pinchtab find "button text"          # 查找元素
pinchtab tabs                        # 获取 Tab 信息
```

### 实例管理

```bash
pinchtab instance start          # 启动新实例
pinchtab instance list            # 列出所有实例
pinchtab instance stop <id>       # 停止实例
pinchtab instance restart <id>    # 重启实例
```

## 配置

### 环境变量

```bash
PINCHTAB_PORT=9868 pinchtab                    # 自定义端口
CHROME_BIN=/path/to/chrome pinchtab            # 自定义 Chrome 路径
PINCHTAB_DATA_DIR=/path/to/data pinchtab       # 自定义数据目录
```

## 故障排除

### 连接被拒绝

```bash
curl http://localhost:9867/health
```

如果失败，启动服务器：
```bash
pinchtab
```

### 端口被占用

```bash
PINCHTAB_PORT=9868 pinchtab
```

### Chrome 未找到

```bash
# macOS
brew install --cask google-chrome

# Linux
sudo apt install chromium-browser
```

## 文档

- **完整文档：** https://pinchtab.com/docs
- **GitHub：** https://github.com/pinchtab/pinchtab
- **Agent 优化：** https://github.com/pinchtab/pinchtab/blob/main/docs/agent-optimization.md

## License

MIT License
