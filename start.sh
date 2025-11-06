#!/bin/bash
# 后端服务启动脚本

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "虚拟环境不存在，请先运行: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，请先配置环境变量"
    echo "运行: cp .env.example .env"
    exit 1
fi

# 启动服务
echo "启动 FastAPI 服务..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
