#!/bin/bash
# PinchTab 快速设置脚本
# 用于在 OpenClaw 环境中安装和配置 PinchTab

set -e

echo "🚀 PinchTab 快速设置"
echo "===================="
echo ""

# 检查 PinchTab 是否已安装
if command -v pinchtab &> /dev/null; then
    echo "✅ PinchTab 已安装"
    pinchtab --version
else
    echo "📦 安装 PinchTab..."
    echo "选择安装方式："
    echo "1) 一键安装（推荐）"
    echo "2) npm 安装"
    read -p "请选择 (1-2): " choice

    case $choice in
        1)
            echo "使用一键安装..."
            curl -fsSL https://pinchtab.com/install.sh | bash
            ;;
        2)
            echo "使用 npm 安装..."
            npm install -g pinchtab
            ;;
        *)
            echo "无效选择，退出"
            exit 1
            ;;
    esac
fi

echo ""
echo "🔍 检查 Chrome/Chromium..."
if [ -d "/Applications/Google Chrome.app" ]; then
    echo "✅ 找到 Google Chrome"
elif command -v chromium &> /dev/null; then
    echo "✅ 找到 Chromium"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ 找到 Chromium"
else
    echo "⚠️  未找到 Chrome/Chromium"
    echo "建议安装："
    echo "  macOS: brew install --cask google-chrome"
    echo "  Linux: sudo apt install chromium-browser"
fi

echo ""
echo "📋 下一步："
echo "1. 启动 PinchTab 服务器："
echo "   pinchtab"
echo ""
echo "2. 启动浏览器实例："
echo "   pinchtab instance start"
echo ""
echo "3. 访问 Dashboard："
echo "   http://localhost:9867/dashboard"
echo ""
echo "4. 导航到页面："
echo "   pinchtab nav https://example.com"
echo ""
echo "5. 检查页面元素："
echo "   pinchtab snap -i -c"
echo ""
echo "✅ 设置完成！"
