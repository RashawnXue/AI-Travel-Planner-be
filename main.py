"""
AI Travel Planner Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import ai, asr, oss, auth, plans, expenses

# 获取配置
settings = get_settings()

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Travel Planner Backend",
    description="后端API服务 - 处理认证、行程、支出、AI、OSS、语音识别等功能",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)      # 认证相关
app.include_router(plans.router)     # 行程管理
app.include_router(expenses.router)  # 支出管理
app.include_router(ai.router)        # AI 生成
app.include_router(asr.router)       # 语音识别
app.include_router(oss.router)       # 文件上传


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Travel Planner Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
