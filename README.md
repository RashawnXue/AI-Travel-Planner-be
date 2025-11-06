# AI Travel Planner Backend

基于 FastAPI 的后端服务，处理 AI、OSS、语音识别等功能。

## 技术栈

- **框架**: FastAPI
- **Python**: 3.10+
- **服务**: 阿里云百炼、OSS、语音识别

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
vi .env  # 填入实际配置
```

### 4. 运行服务

```bash
# 开发模式（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
AI-Travel-Planner-be/
├── main.py              # FastAPI 主应用
├── requirements.txt     # Python 依赖
├── .env                 # 环境变量（不提交）
├── .env.example         # 环境变量模板
├── app/
│   ├── __init__.py
│   ├── config.py        # 配置管理
│   ├── routers/         # API 路由
│   │   ├── __init__.py
│   │   ├── ai.py        # AI 相关接口
│   │   ├── asr.py       # 语音识别接口
│   │   └── oss.py       # OSS 相关接口
│   └── services/        # 业务逻辑
│       ├── __init__.py
│       ├── ai_service.py
│       ├── asr_service.py
│       └── oss_service.py
└── README.md
```

## 环境变量

```bash
# 阿里云百炼
BAILIAN_API_KEY=your_api_key
BAILIAN_APP_ID=your_app_id
BAILIAN_MODEL_NAME=qwen-max

# 阿里云 OSS
OSS_REGION=oss-cn-shanghai
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET=your_bucket_name

# CORS 设置
CORS_ORIGINS=http://localhost:5173,http://localhost
```

## 部署

### Docker 部署

```bash
docker build -t ai-travel-planner-be .
docker run -d -p 8000:8000 --env-file .env ai-travel-planner-be
```

### Nginx 反向代理

前端 Nginx 配置中添加：

```nginx
location /api/backend/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```
