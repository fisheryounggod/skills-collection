# PinchTab 快速使用指南

## 📊 当前状态

✅ **PinchTab 已安装：** pinchtab 0.7.8
✅ **服务器运行中：** http://localhost:9867/dashboard
✅ **浏览器实例已启动：** inst_d364e51b (headless)
✅ **已测试导航：** https://example.com

---

## 🚀 常用命令

### 服务器管理

```bash
# 启动服务器
bash skills/pinchtab/scripts/start.sh

# 停止服务器
kill $(cat ~/.config/PinchTab/pinchtab.pid)

# 查看日志
tail -f ~/.config/PinchTab/pinchtab.log
```

### 浏览器实例

```bash
# 启动新实例
pinchtab instance start

# 列出所有实例
pinchtab instance list

# 停止实例
pinchtab instance stop <instance_id>
```

### 页面导航

```bash
# 导航到 URL
pinchtab nav <url>

# 示例
pinchtab nav https://github.com
pinchtab nav https://example.com/form
```

### 页面检查

```bash
# 获取交互式元素（推荐，节省 token）
pinchtab snap -i -c

# 完整快照
pinchtab snap

# 获取页面文本
pinchtab text
```

### 元素交互

```bash
# 点击元素
pinchtab click <ref>

# 输入文本
pinchtab type <ref> "text"

# 填充表单
pinchtab fill <ref> "value"

# 按键
pinchtab press Enter

# 悬停
pinchtab hover <ref>

# 滚动
pinchtab scroll down
```

### 输出

```bash
# 截图
pinchtab screenshot /tmp/screenshot.png

# 导出 PDF
pinchtab pdf /tmp/page.pdf
```

---

## 📝 完整工作流示例

### 场景 1：自动填写表单

```bash
# 1. 导航到表单页面
pinchtab nav https://example.com/form

# 2. 获取页面元素
pinchtab snap -i -c

# 输出示例：
# e0:textbox "Name"
# e1:textbox "Email"
# e2:button "Submit"

# 3. 填写表单
pinchtab type e0 "John Doe"
pinchtab type e1 "john@example.com"

# 4. 提交表单
pinchtab click e2

# 5. 验证结果
pinchtab screenshot /tmp/form-submitted.png
```

### 场景 2：网页数据抓取

```bash
# 1. 导航到目标页面
pinchtab nav https://example.com/products

# 2. 获取页面文本
pinchtab text > /tmp/page-content.txt

# 3. 获取页面结构
pinchtab snap -i -c > /tmp/page-structure.json
```

### 场景 3：页面测试

```bash
# 1. 导航到测试页面
pinchtab nav https://example.com/login

# 2. 截图保存
pinchtab screenshot /tmp/before-click.png

# 3. 执行操作
pinchtab type e0 "test@example.com"
pinchtab type e1 "password123"
pinchtab click e2

# 4. 等待加载并截图验证
sleep 2
pinchtab screenshot /tmp/after-click.png
```

---

## 🐍 Python API 使用

```python
from skills.pinchtab.scripts.pinchtab import PinchTab

# 创建浏览器实例
browser = PinchTab()

# 导航到页面
browser.nav("https://example.com")

# 获取页面快照
snapshot = browser.snap(interactive=True, compact=True)
print(f"Found {len(snapshot['nodes'])} elements")

# 遍历元素
for node in snapshot['nodes']:
    print(f"{node['role']}: {node['name']} (ref: {node['ref']})")

# 点击第一个元素
if snapshot['nodes']:
    first_ref = snapshot['nodes'][0]['ref']
    browser.click(first_ref)

# 输入文本
browser.type("e0", "Hello, World!")

# 截图
browser.screenshot("/tmp/screenshot.png")

# 获取页面文本
text_data = browser.text()
print(text_data)
```

---

## 🌟 高级功能

### JavaScript 执行

```bash
# 执行自定义 JavaScript
pinchtab eval "document.title"

# 修改页面样式
pinchtab eval "document.body.style.backgroundColor = 'yellow'"
```

### 多实例管理

```bash
# 启动多个实例（用于并行任务）
pinchtab instance start
pinchtab instance start
pinchtab instance start

# 列出所有实例
pinchtab instance list

# 停止特定实例
pinchtab instance stop <instance_id>
```

### 配置文件使用

```bash
# 使用特定配置文件启动实例
pinchtab instance start --profile my-profile
```

---

## 📖 更多资源

- **Dashboard：** http://localhost:9867/dashboard
- **完整文档：** https://pinchtab.com/docs
- **Agent 优化：** https://github.com/pinchtab/pinchtab/blob/main/docs/agent-optimization.md
- **GitHub：** https://github.com/pinchtab/pinchtab

---

## 🛠 故障排除

### 问题：连接被拒绝

```bash
# 检查服务器是否运行
curl http://localhost:9867/health

# 如果失败，重新启动
bash skills/pinchtab/scripts/start.sh
```

### 问题：端口被占用

```bash
# 使用不同端口启动
PINCHTAB_PORT=9868 pinchtab
```

### 问题：实例启动失败

```bash
# 查看日志
tail -f ~/.config/PinchTab/pinchtab.log

# 重启服务器
kill $(cat ~/.config/PinchTab/pinchtab.pid)
bash skills/pinchtab/scripts/start.sh
```

---

## ✅ 当前配置摘要

- **PinchTab 版本：** 0.7.8
- **服务器地址：** http://localhost:9867
- **Dashboard：** http://localhost:9867/dashboard
- **Health Check：** http://localhost:9867/health
- **日志文件：** ~/.config/PinchTab/pinchtab.log
- **浏览器：** Google Chrome (headless)

---

**准备好了！开始使用 PinchTab 控制浏览器吧！** 🦀
