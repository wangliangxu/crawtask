#!/bin/bash

# 一键启动脚本 - 同时启动前端和后端
echo "========================================="
echo "     爬虫任务管理系统启动脚本"
echo "========================================="

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..."

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "前端依赖未安装，正在安装..."
    ./build_frontend.sh
    if [ $? -ne 0 ]; then
        echo "前端依赖安装失败!"
        exit 1
    fi
fi

# 检查后端依赖
echo "检查后端依赖..."
cd backend
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "后端依赖未安装，正在安装..."
    cd ..
    ./install_backend.sh
    if [ $? -ne 0 ]; then
        echo "后端依赖安装失败!"
        exit 1
    fi
    cd backend
fi

cd ..

echo "启动服务..."

# 创建日志目录
mkdir -p logs

# 启动后端服务（在后台）
echo "启动后端服务..."
cd backend
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务PID: $BACKEND_PID"
cd ..

# 等待后端服务启动
sleep 3

# 启动前端开发服务器（在后台）
echo "启动前端服务..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务PID: $FRONTEND_PID"
cd ..

# 保存PID到文件以便后续管理
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo ""
echo "========================================="
echo "服务启动完成!"
echo "后端API: http://localhost:8000"
echo "前端页面: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "日志文件位置:"
echo "后端日志: logs/backend.log"
echo "前端日志: logs/frontend.log"
echo ""
echo "停止服务请运行: ./stop_services.sh"
echo "========================================="

# 显示实时日志（可选）
read -p "是否查看实时日志？(y/n): " show_logs
if [ "$show_logs" = "y" ] || [ "$show_logs" = "Y" ]; then
    echo "按 Ctrl+C 退出日志查看..."
    tail -f logs/backend.log logs/frontend.log
fi