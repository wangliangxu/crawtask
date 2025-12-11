# CrawTask - 分布式爬虫任务管理平台

CrawTask 是一个现代化的分布式爬虫任务管理与监控系统。它旨在通过 SSH 协议统一管理部署在多台服务器上的爬虫进程，无需在目标机器上安装 Agent。系统支持实时日志监控、自动健康巡检、以及灵活的节点管理（支持跳板机模式）。

## 🌟 核心功能

- **无 Agent 管理**: 基于 SSH 协议，直接连接服务器进行进程控制和日志获取。
- **实时日志监控**: 基于 WebSocket 的实时日志流传输，提供 Web 端类似 Terminal 的查看体验。
- **智能健康巡检**:
  - 自动分析日志头部/尾部时间戳，判断任务是否假死（>1小时无日志视为 Stopped）。
  - 支持关键词（如 "Exception"）和错误率检测（Error > 40%），自动标记任务健康状态。
- **中心节点支持 (Jump Host)**: 支持配置中心节点（Center Node），并通过 SSH 隧道访问内网的其他节点。
- **系统配置管理**: 支持在线修改系统级参数（如巡检间隔）。
- **批量任务与编辑**: 支持批量创建任务，以及对现有任务进行编辑配置。

## 🛠 技术栈

### Backend (后端)
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **SSH Library**: asyncssh (高性能异步 SSH)
- **Database**: SQLite (SQLAlchemy ORM)
- **Task Queue**: APScheduler

### Frontend (前端)
- **Framework**: React 19 + TypeScript + Vite
- **UI Library**: Ant Design v6
- **Terminal**: Xterm.js

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+

### 1. 后端启动 (Backend)

进入 backend 目录：
```bash
cd backend
```

创建虚拟环境并安装依赖：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

初始化数据库（首次运行）：
```bash
python migrate_db.py
```

启动服务：
```bash
uvicorn app.main:app --reload
```
后端服务将运行在 `http://127.0.0.1:8000`。

### 2. 前端启动 (Frontend)

进入 frontend 目录：
```bash
cd frontend
```

安装依赖：
```bash
npm install
```

启动开发服务器：
```bash
npm run dev
```
访问前端页面：`http://localhost:5173`。

## 📖 使用指南

### 1. 配置节点 (Nodes)
在 "Node Management" 页面添加你的爬虫服务器。
- **Host**: 服务器 IP。
- **Username**: SSH 用户名 (可选，若不填则尝试读取 `~/.ssh/config` 或使用当前系统用户)。
- **Port**: 端口 (可选，默认 22 或读取 config)。
- **Auth**: 支持密码或私钥路径。
- **Center Node**: 如果你的目标服务器在内网，可以先添加一台公网跳板机并标记为 "Center Node"。后续添加内网机器时，系统会自动通过该跳板机连接。

### 2. 创建任务 (Tasks)
在 "Tasks" 页面点击 "Add Task"。
- **Node**: 选择一个或多个节点。
- **Log Path**: 指定远程服务器上的日志文件绝对路径（必须存在）。
- **Health Check**: 设置触发 Error 状态的关键词 (如 `Traceback`).
- **Commands**: 设置 Start/Stop 命令 (支持 shell 命令，如 `systemctl start my_spider` 或 `python main.py &`).

### 3. 监控与运维
- **状态查看**: 列表页实时刷新任务状态 (Running/Stopped) 和健康度 (Healthy/Error)。
- **实时日志**: 点击 "Logs" 按钮，通过 WebSocket 查看实时日志流。
- **操作**: 支持一键 Start/Stop/Restart/Delete，以及 **Edit** 修改任务配置。
- **启用/禁用**: 可通过 Switch 开关暂时禁用某个任务，禁用后系统不再对其进行后台健康巡检。

## 📄 License
MIT
