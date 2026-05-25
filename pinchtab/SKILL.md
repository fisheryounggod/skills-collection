# PinchTab - 浏览器控制工具

## 描述

PinchTab 是一个独立的 HTTP 服务器，通过 CLI 和 HTTP API 直接控制 Chrome。为 AI agent、脚本和自动化工作流提供浏览器控制能力。

**网站：** https://pinchtab.com
**GitHub：** https://github.com/pinchtab/pinchtab

## 核心特性

- **Server-first 架构**：主进程是控制平面服务器
- **Tab 级别交互**：所有操作在标签页级别进行
- **状态持久化**：配置文件保存 cookies 和浏览器状态
- **Token 高效**：快照和文本端点比截图驱动的工作流更节省 token
- **多实例编排**：同时管理多个浏览器实例
- **灵活部署**：支持 headless、headed、profile-backed 或附加现有 Chrome

## 安装

### 方式 1：一键安装（推荐，macOS/Linux）

```bash
curl -fsSL https://pinchtab.com/install.sh | bash
pinchtab --version
```

### 方式 2：npm 安装

**要求：** Node.js 18+

```bash
npm install -g pinchtab
pinchtab --version
```

### 方式 3：Docker

```bash
docker run -d -p 9867:9867 pinchtab/pinchtab
curl http://localhost:9867/health
```

### 方式 4：从源码构建

**要求：** Go 1.25+, Git, Chrome/Chromium

```bash
git clone https://github.com/pinchtab/pinchtab.git
cd pinchtab
./pdev doctor
go build -o pinchtab ./cmd/pinchtab
./pinchtab --version
```

## 快速开始

### 1. 启动服务器

```bash
pinchtab
```

服务器运行在 `http://127.0.0.1:9867`，可以访问 Dashboard：
- http://127.0.0.1:9867
- http://127.0.0.1:9867/dashboard

### 2. 启动实例

```bash
pinchtab instance start
```

返回示例：
```json
{
  "id": "inst_0a89a5bb",
  "profileId": "prof_278be873",
  "profileName": "instance-1741400000000000000",
  "port": "9868",
  "headless": true,
  "status": "starting"
}
```

### 3. 导航到页面

```bash
pinchtab nav https://example.com
```

### 4. 检查页面元素

```bash
pinchtab snap -i -c
```

返回示例：
```json
{
  "nodes": [
    { "ref": "e0", "role": "link", "name": "Docs" },
    { "ref": "e1", "role": "button", "name": "Get started" }
  ]
}
```

### 5. 点击元素

```bash
pinchtab click e1
```

## 主要命令

### 服务器管理

```bash
# 启动服务器
pinchtab

# 使用自定义端口
PINCHTAB_PORT=9868 pinchtab
```

### 实例管理

```bash
# 启动新实例
pinchtab instance start

# 列出所有实例
pinchtab instance list

# 停止实例
pinchtab instance stop <instance_id>

# 重启实例
pinchtab instance restart <instance_id>
```

### 导航和页面操作

```bash
# 导航到 URL
pinchtab nav <url>

# 刷新页面
pinchtab reload

# 后退/前进
pinchtab back
pinchtab forward
```

### 页面检查

```bash
# 快照（交互式元素）
pinchtab snap -i -c

# 完整快照（包含所有元素）
pinchtab snap

# 文本模式快照
pinchtab snap -t

# 获取页面文本
pinchtab text
```

### 元素交互

```bash
# 点击元素（通过 ref）
pinchtab click <ref>

# 输入文本
pinchtab type <ref> "text"

# 填充表单
pinchtab fill <ref> "value"

# 按键
pinchtab press Enter
pinchtab press Escape

# 悬停
pinchtab hover <ref>

# 聚焦
pinchtab focus <ref>

# 选择文本
pinchtab select <ref>

# 滚动
pinchtab scroll down
pinchtab scroll up
pinchtab scroll top
pinchtab scroll bottom
```

### 输出

```bash
# 截图
pinchtab screenshot <output_path>

# 导出 PDF
pinchtab pdf <output_path>
```

### 高级功能

```bash
# 执行 JavaScript
pinchtab eval "document.title"

# 查找元素
pinchtab find "button text"

# 获取 Tab 信息
pinchtab tabs
```

## Python API 封装示例

创建 `skills/pinchtab/scripts/pinchtab.py`：

```python
#!/usr/bin/env python3
import subprocess
import json
import sys

class PinchTab:
    def __init__(self):
        self.base_cmd = ["pinchtab"]

    def nav(self, url):
        """导航到 URL"""
        result = subprocess.run(self.base_cmd + ["nav", url], capture_output=True, text=True)
        return json.loads(result.stdout)

    def snap(self, interactive=True, compact=False):
        """页面快照"""
        cmd = self.base_cmd + ["snap"]
        if interactive:
            cmd.append("-i")
        if compact:
            cmd.append("-c")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

    def click(self, ref):
        """点击元素"""
        result = subprocess.run(self.base_cmd + ["click", ref], capture_output=True, text=True)
        return json.loads(result.stdout)

    def type(self, ref, text):
        """输入文本"""
        result = subprocess.run(self.base_cmd + ["type", ref, text], capture_output=True, text=True)
        return json.loads(result.stdout)

    def screenshot(self, path):
        """截图"""
        result = subprocess.run(self.base_cmd + ["screenshot", path], capture_output=True, text=True)
        return json.loads(result.stdout)

    def text(self):
        """获取页面文本"""
        result = subprocess.run(self.base_cmd + ["text"], capture_output=True, text=True)
        return json.loads(result.stdout)

# 使用示例
if __name__ == "__main__":
    browser = PinchTab()

    # 导航
    browser.nav("https://example.com")

    # 快照
    snapshot = browser.snap(interactive=True, compact=True)
    print(f"Found {len(snapshot['nodes'])} elements")

    # 如果有按钮，点击它
    if snapshot['nodes']:
        first_ref = snapshot['nodes'][0]['ref']
        browser.click(first_ref)
```

## 常见使用场景

### 场景 1：自动化表单填写

```bash
# 打开表单页面
pinchtab nav https://example.com/form

# 获取快照
pinchtab snap -i -c > snapshot.json

# 填写输入框
pinchtab type e0 "John Doe"
pinchtab type e1 "john@example.com"

# 点击提交
pinchtab click e2
```

### 场景 2：网页数据抓取

```python
import json
from skills.pinchtab.pinchtab import PinchTab

browser = PinchTab()
browser.nav("https://example.com/data")

# 获取页面文本
text_data = browser.text()
print(text_data)

# 或快照
snapshot = browser.snap(interactive=True, compact=True)
for node in snapshot['nodes']:
    print(f"{node['role']}: {node['name']}")
```

### 场景 3：截图和 PDF 导出

```bash
# 导航到页面
pinchtab nav https://example.com

# 截图
pinchtab screenshot /tmp/screenshot.png

# 导出 PDF
pinchtab pdf /tmp/page.pdf
```

## 配置

### 环境变量

```bash
# 自定义端口
PINCHTAB_PORT=9868 pinchtab

# 指定 Chrome 路径
CHROME_BIN=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome pinchtab

# 自定义数据目录
PINCHTAB_DATA_DIR=/path/to/data pinchtab
```

### 配置文件

配置文件位置：
- macOS: `~/Library/Application Support/PinchTab/`
- Linux: `~/.config/PinchTab/`

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
brew install chromium

# Linux (Ubuntu/Debian)
sudo apt install chromium-browser

# 自定义 Chrome 路径
CHROME_BIN=/path/to/chrome pinchtab
```

## 依赖要求

- **Chrome/Chromium**：浏览器引擎
- **Node.js 18+**（如果使用 npm 安装）
- **Go 1.25+**（如果从源码构建）
- **Docker**（可选，用于 Docker 部署）

## 参考文档

- **官方文档：** https://pinchtab.com/docs
- **GitHub：** https://github.com/pinchtab/pinchtab
- **Agent 优化：** https://github.com/pinchtab/pinchtab/blob/main/docs/agent-optimization.md
- **支持：**
  - GitHub Issues: https://github.com/pinchtab/pinchtab/issues
  - GitHub Discussions: https://github.com/pinchtab/pinchtab/discussions
  - X: https://x.com/pinchtabdev

## License

MIT License
