#!/usr/bin/env python3
"""
PinchTab Python 封装
为 OpenClaw 提供更易用的 PinchTab 接口
"""

import subprocess
import json
import sys
from pathlib import Path


class PinchTab:
    """PinchTab 浏览器控制封装"""

    def __init__(self):
        self.base_cmd = ["pinchtab"]

    def _run(self, args, capture=True):
        """运行 PinchTab 命令"""
        cmd = self.base_cmd + args
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True
        )
        if capture:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout}
        return result.returncode == 0

    def nav(self, url):
        """导航到 URL"""
        return self._run(["nav", url])

    def snap(self, interactive=True, compact=False):
        """页面快照

        Args:
            interactive: 只返回交互式元素
            compact: 紧凑格式（推荐）

        Returns:
            包含 nodes 列表的字典
        """
        args = ["snap"]
        if interactive:
            args.append("-i")
        if compact:
            args.append("-c")
        return self._run(args)

    def click(self, ref):
        """点击元素

        Args:
            ref: 元素引用（如 e0, e1）
        """
        return self._run(["click", ref])

    def type(self, ref, text):
        """输入文本

        Args:
            ref: 输入框元素引用
            text: 要输入的文本
        """
        return self._run(["type", ref, text])

    def fill(self, ref, value):
        """填充表单字段

        Args:
            ref: 字段元素引用
            value: 字段值
        """
        return self._run(["fill", ref, value])

    def press(self, key):
        """按键

        Args:
            key: 按键名称（Enter, Escape, Tab 等）
        """
        return self._run(["press", key])

    def hover(self, ref):
        """悬停

        Args:
            ref: 元素引用
        """
        return self._run(["hover", ref])

    def focus(self, ref):
        """聚焦元素

        Args:
            ref: 元素引用
        """
        return self._run(["focus", ref])

    def select(self, ref):
        """选择元素

        Args:
            ref: 元素引用
        """
        return self._run(["select", ref])

    def scroll(self, direction="down"):
        """滚动页面

        Args:
            direction: 方向（up, down, top, bottom）
        """
        return self._run(["scroll", direction])

    def screenshot(self, path):
        """截图

        Args:
            path: 输出文件路径
        """
        return self._run(["screenshot", path])

    def pdf(self, path):
        """导出 PDF

        Args:
            path: 输出 PDF 文件路径
        """
        return self._run(["pdf", path])

    def text(self):
        """获取页面文本"""
        return self._run(["text"])

    def eval_js(self, code):
        """执行 JavaScript

        Args:
            code: JavaScript 代码
        """
        return self._run(["eval", code])

    def find(self, selector):
        """查找元素

        Args:
            selector: 选择器或文本
        """
        return self._run(["find", selector])

    def health(self):
        """检查服务器健康状态"""
        return self._run(["health"])

    def instance_start(self):
        """启动新实例"""
        return self._run(["instance", "start"])

    def instance_list(self):
        """列出所有实例"""
        return self._run(["instance", "list"])

    def instance_stop(self, instance_id):
        """停止实例"""
        return self._run(["instance", "stop", instance_id])


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python pinchtab.py <command> [args...]")
        print("Commands: nav, snap, click, type, fill, press, screenshot, pdf, text")
        sys.exit(1)

    command = sys.argv[1]
    browser = PinchTab()

    if command == "nav":
        result = browser.nav(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "snap":
        interactive = "-i" in sys.argv
        compact = "-c" in sys.argv
        result = browser.snap(interactive=interactive, compact=compact)
        print(json.dumps(result, indent=2))

    elif command == "click":
        result = browser.click(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "type":
        if len(sys.argv) < 4:
            print("Usage: python pinchtab.py type <ref> <text>")
            sys.exit(1)
        result = browser.type(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))

    elif command == "fill":
        if len(sys.argv) < 4:
            print("Usage: python pinchtab.py fill <ref> <value>")
            sys.exit(1)
        result = browser.fill(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))

    elif command == "press":
        if len(sys.argv) < 3:
            print("Usage: python pinchtab.py press <key>")
            sys.exit(1)
        result = browser.press(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "screenshot":
        if len(sys.argv) < 3:
            print("Usage: python pinchtab.py screenshot <path>")
            sys.exit(1)
        result = browser.screenshot(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "pdf":
        if len(sys.argv) < 3:
            print("Usage: python pinchtab.py pdf <path>")
            sys.exit(1)
        result = browser.pdf(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "text":
        result = browser.text()
        print(json.dumps(result, indent=2))

    elif command == "scroll":
        direction = sys.argv[2] if len(sys.argv) > 2 else "down"
        result = browser.scroll(direction)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
