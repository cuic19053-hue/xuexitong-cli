@echo off
chcp 65001 >nul
title Xuexitong CLI 学习通自动化管家

echo ======================================================
echo    Xuexitong CLI (学习通全自动刷课与作业助手)
echo ======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python 环境，请先安装 Python 并勾选 Add Python to PATH！
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 requests
python -c "import requests" >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] 正在安装必要网络依赖库 requests...
    python -m pip install requests
)

echo.
echo [1] 一键全自动管家 (自动登录 + 找课刷课 + AI写作业)
echo [2] 仅扫码登录 / 检查登录状态
echo [3] 退出
echo.
set /p choice="请选择模式 (默认按回车选 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" (
    echo.
    echo 正在启动全自动巡航...
    python bin\auto_run.py
) else if "%choice%"=="2" (
    echo.
    python bin\xuexitong auth --poll
) else (
    exit /b 0
)

pause
