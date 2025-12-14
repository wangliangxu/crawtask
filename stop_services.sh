#!/bin/bash

# 停止所有服务脚本
echo "========================================="
echo "     爬虫任务管理系统停止脚本"
echo "========================================="

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "后端服务已停止"
    else
        echo "后端服务未运行或PID文件无效"
    fi
    rm -f logs/backend.pid
else
    echo "未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "前端服务已停止"
    else
        echo "前端服务未运行或PID文件无效"
    fi
    rm -f logs/frontend.pid
else
    echo "未找到前端服务PID文件"
fi

# 强制停止残留进程
echo "检查并停止残留进程..."
pkill -f "python3 main.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

echo "所有服务已停止!"