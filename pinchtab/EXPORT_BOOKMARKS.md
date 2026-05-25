# 使用 PinchTab 导出 X 收藏夹

## 前提条件

✅ **PinchTab 已安装并运行**
✅ **需要先登录 X 账号**

---

## 方法 1：自动导出（推荐）

### 步骤 1：先登录 X

访问 PinchTab Dashboard 并手动登录：

```bash
# 1. 访问 Dashboard
open http://localhost:9867/dashboard

# 2. 找到运行中的实例
# 3. 点击实例，在浏览器中打开
# 4. 访问 https://x.com 并登录
```

### 步骤 2：运行导出脚本

```bash
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py auto
```

脚本会：
1. 导航到 https://x.com/i/bookmarks
2. 获取页面快照
3. 提取收藏链接
4. 生成三个格式的导出文件

### 步骤 3：查看导出结果

```bash
# 查看 JSON 格式
cat /tmp/twitter_bookmarks.json

# 查看 Markdown 格式
cat /tmp/twitter_bookmarks.md

# 查看文本格式
cat /tmp/twitter_bookmarks.txt
```

---

## 方法 2：手动输入

如果自动提取失败，可以手动输入：

```bash
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py manual
```

然后逐个输入：
- 收藏链接
- 收藏名称

---

## 方法 3：获取页面文本

如果只想保存页面原始内容：

```bash
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py text
```

---

## 导出文件位置

所有文件保存在 `/tmp/` 目录：

- `twitter_bookmarks.json` - JSON 格式
- `twitter_bookmarks.md` - Markdown 格式（适合笔记）
- `twitter_bookmarks.txt` - 纯文本格式
- `twitter_bookmarks_page_text.txt` - 页面原始文本

---

## 完整示例流程

### 1. 确保服务器运行

```bash
curl http://localhost:9867/health
```

### 2. 启动实例（如果没有）

```bash
pinchtab instance start
```

### 3. 访问 Dashboard 并登录

```bash
open http://localhost:9867/dashboard
```

在浏览器中登录 https://x.com

### 4. 运行导出

```bash
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py auto
```

### 5. 处理导出文件

```bash
# 复制到工作区
cp /tmp/twitter_bookmarks.md ~/Documents/

# 或查看内容
cat /tmp/twitter_bookmarks.json | jq
```

---

## 常见问题

### Q: 为什么找不到链接？

A: 可能的原因：
1. 页面还未完全加载
2. 需要滚动页面加载更多收藏
3. 收藏列表使用不同的结构
4. 未登录 X 账号

解决方法：
- 使用 `text` 模式获取页面文本
- 手动使用 `manual` 模式输入链接

### Q: 如何处理大量收藏？

A: 脚本限制每次处理前 10 个链接，避免超时。

如果要导出所有收藏：
1. 多次运行脚本
2. 或修改脚本中的循环限制
3. 或使用 `text` 模式获取完整页面

### Q: 能导出到飞书吗？

A: 可以！将 Markdown 文件上传到飞书：

```bash
# 将 MD 文件上传到飞书（需要飞书 CLI 或 API）
# 或者：
cat /tmp/twitter_bookmarks.md | pbcopy  # 复制到剪贴板
# 然后粘贴到飞书文档
```

---

## 高级用法

### Python API 直接使用

```python
from skills.pinchtab.scripts.pinchtab import PinchTab

browser = PinchTab()

# 1. 导航到收藏页面
browser.nav("https://x.com/i/bookmarks")

# 2. 获取页面文本
text_data = browser.text()

# 3. 保存到文件
with open("/tmp/bookmarks.txt", "w") as f:
    f.write(text_data)

print("✅ 页面文本已保存")
```

---

## 命令参考

```bash
# 自动导出
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py auto

# 手动输入
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py manual

# 获取页面文本
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py text

# 显示帮助
python3 skills/pinchtab/scripts/export-twitter-bookmarks.py help
```

---

## 注意事项

⚠️ **重要：**
1. 必须先在 X 登录账号
2. 页面需要完全加载
3. 可能需要多次滚动加载所有收藏
4. 导出基于页面快照，可能无法获取所有链接

💡 **建议：**
- 对于大量收藏，考虑使用 X API（需要 API Key）
- 或使用 browser automation tool 专门处理滚动
- 定期导出备份

---

## 下一步

导出后，你可以：
1. 整理收藏链接
2. 创建分类（按主题、时间等）
3. 上传到飞书或 Notion 等笔记工具
4. 与其他收藏夹对比合并

---

需要我帮你运行导出脚本吗？
