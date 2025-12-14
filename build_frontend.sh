#!/bin/bash

# 前端构建脚本
echo "开始构建前端项目..."

# 检查Node.js和npm是否安装
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装，请先安装 Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装，请先安装 npm"
    exit 1
fi

# 进入前端目录
cd frontend

echo "安装前端依赖..."
npm install

echo "构建前端项目..."
npm run build

if [ $? -eq 0 ]; then
    echo "前端构建成功!"
    echo "构建文件位置: frontend/dist/"
    
    # 检查构建输出目录
    if [ -d "dist" ]; then
        echo "构建文件详情:"
        ls -la dist/
    fi
else
    echo "前端构建失败!"
    exit 1
fi

echo "前端构建完成!"