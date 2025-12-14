#!/bin/bash

# 后端依赖安装脚本
echo "开始安装后端依赖..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装，请先安装 Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: pip3 未安装，请先安装 pip3"
    exit 1
fi

echo "Python版本: $(python3 --version)"
echo "pip版本: $(pip3 --version)"

# 进入后端目录
cd backend

echo "创建虚拟环境（可选）..."
read -p "是否创建虚拟环境？(y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "虚拟环境创建成功"
    fi
    source venv/bin/activate
    echo "已激活虚拟环境"
fi

echo "升级pip..."
pip3 install --upgrade pip

echo "安装后端依赖..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "警告: requirements.txt 文件不存在"
fi

echo "验证安装..."
pip3 list

if [ $? -eq 0 ]; then
    echo "后端依赖安装成功!"
else
    echo "后端依赖安装失败!"
    exit 1
fi

echo "后端依赖安装完成!"