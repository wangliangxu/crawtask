#!/bin/bash

# Docker构建和部署脚本
echo "========================================="
echo "     Docker构建和部署脚本"
echo "========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 选择部署模式
echo "选择部署模式:"
echo "1. 开发环境 (development)"
echo "2. 生产环境 (production)"
echo "3. 仅构建镜像 (build only)"
read -p "请输入选择 (1-3): " mode

case $mode in
    1)
        echo "构建开发环境..."
        cd docker
        docker-compose build
        echo "启动开发环境..."
        docker-compose up -d
        echo "开发环境启动完成!"
        echo "后端API: http://localhost:8000"
        echo "前端页面: http://localhost:5173"
        ;;
    2)
        echo "构建生产环境..."
        # 构建前端
        echo "构建前端..."
        cd frontend
        npm install
        npm run build
        cd ..
        
        # 构建Docker镜像
        cd docker
        docker-compose -f docker-compose.yml --profile production build
        echo "启动生产环境..."
        docker-compose --profile production up -d
        cd ..
        echo "生产环境启动完成!"
        echo "前端页面: http://localhost"
        echo "后端API: http://localhost/api"
        ;;
    3)
        echo "仅构建Docker镜像..."
        cd docker
        docker-compose build
        cd ..
        echo "镜像构建完成!"
        ;;
    *)
        echo "无效选择!"
        exit 1
        ;;
esac

# 显示容器状态
echo ""
echo "容器状态:"
cd docker
docker-compose ps
cd ..