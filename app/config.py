"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    
    # 阿里云百炼
    bailian_api_key: str = ""  # 可选，优先使用用户提供的 key
    bailian_app_id: str
    bailian_model_name: str = "qwen-max"
    
    # 阿里云 OSS
    oss_region: str
    oss_access_key_id: str
    oss_access_key_secret: str
    oss_bucket: str
    
    # JWT 配置（用于 session token）
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 天
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost"
    
    # 服务配置
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS origins 字符串转为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    return Settings()
