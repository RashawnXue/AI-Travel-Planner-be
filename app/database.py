"""
数据库连接管理模块 - Supabase 客户端单例
"""
from supabase import create_client, Client
from app.config import Settings

# 全局单例客户端
_supabase_client: Client = None


def get_supabase_client(settings: Settings) -> Client:
    """
    获取 Supabase 客户端单例
    
    使用全局变量确保整个应用生命周期中只创建一次客户端
    这样可以：
    1. 复用连接，减少建立连接的开销
    2. 提升请求响应速度
    3. 减少资源消耗
    
    Args:
        settings: 应用配置
        
    Returns:
        Supabase 客户端实例
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    return _supabase_client
