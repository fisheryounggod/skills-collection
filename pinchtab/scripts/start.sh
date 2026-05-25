#!/bin/bash
# PinchTab 启动脚本
# 后台启动 PinchTab 服务器

set -e

PINCHTAB_DIR="$HOME/.config/PinchTab"
PID_FILE="$PINCHTAB_DIR/pinchtab.pid"
LOG_FILE="$PINCHTAB_DIR/pinchtab.log"

# 创建目录
mkdir -p "$PINCHTAB_DIR"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ PinchTab 已在运行 (PID: $PID)"
        echo "   Dashboard: http://localhost:9867/dashboard"
        exit 0
    else
        echo "清理旧的 PID 文件..."
        rm "$PID_FILE"
    fi
fi

echo "🚀 启动 PinchTab 服务器..."

# 后台启动并记录 PID
nohup pinchtab > "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

# 等待启动
sleep 2

# 检查是否成功启动
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ PinchTab 启动成功！"
    echo ""
    echo "📊 Dashboard: http://localhost:9867/dashboard"
    echo "🏥 Health:   http://localhost:9867/health"
    echo ""
    echo "📋 快速命令："
    echo "   pinchtab instance start        # 启动浏览器实例"
    echo "   pinchtab nav <url>          # 导航到页面"
    echo "   pinchtab snap -i -c         # 检查页面元素"
    echo "   pinchtab click <ref>         # 点击元素"
    echo ""
    echo "📝 日志文件: $LOG_FILE"
    echo "🛑 停止服务: kill $(cat $PID_FILE)"
else
    echo "❌ PinchTab 启动失败，查看日志："
    cat "$LOG_FILE"
    exit 1
fi
