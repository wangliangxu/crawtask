# 多阶段构建 - 生产环境优化
FROM node:18-alpine as frontend-build

# 设置工作目录
WORKDIR /app/frontend

# 复制前端包配置文件
COPY ../frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制前端源代码
COPY ../frontend/ .

# 构建前端
RUN npm run build

# Python后端镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制后端requirements文件
COPY ../backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源代码
COPY ../backend/ ./backend/

# 复制前端构建结果
COPY --from=frontend-build /app/frontend/dist ./backend/static/

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]