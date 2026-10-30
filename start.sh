#!/usr/bin/env bash
cd "$(dirname "$0")"

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ [错误] 系统中未找到 Python 环境，请先安装 Python 3！"
    exit 1
fi

$PYTHON_CMD -c "import requests" &>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 [提示] 正在安装网络依赖 requests..."
    $PYTHON_CMD -m pip install requests
fi

chmod +x bin/xuexitong bin/auto_run.py 2>/dev/null

echo "======================================================"
echo "   Xuexitong CLI (学习通全自动刷课与作业助手)"
echo "   系统环境: $(uname -s)"
echo "======================================================"
echo ""
echo " [1] 一键全自动管家 (自动登录 + 找课刷课 + AI写作业)"
echo " [2] 仅扫码登录 / 检查登录状态"
echo " [3] 退出"
echo ""
read -p "请选择模式 (默认按回车选 1): " choice

choice=${choice:-1}

if [ "$choice" = "1" ]; then
    echo ""
    echo "🚀 正在启动全自动巡航..."
    $PYTHON_CMD bin/auto_run.py
elif [ "$choice" = "2" ]; then
    echo ""
    $PYTHON_CMD bin/xuexitong auth --poll
else
    exit 0
fi
