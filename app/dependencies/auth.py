"""
认证依赖和中间件
"""
from fastapi import Header, HTTPException, Depends
from typing import Optional
from app.config import get_settings, Settings
from app.services.auth_service import AuthService


async def get_current_user(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> dict:
    """
    从 Authorization header 中获取当前用户
    
    Args:
        authorization: Authorization header (Bearer token)
        settings: 配置
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 如果token无效或缺失
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="未提供认证信息"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="认证格式错误，应为: Bearer <token>"
        )
    
    token = authorization[7:]  # 移除 "Bearer " 前缀
    
    try:
        auth_service = AuthService(settings)
        user = await auth_service.get_user(token)
        
        # 将 token 附加到用户信息中，供后续使用
        user["access_token"] = token
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"认证失败: {str(e)}"
        )


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> Optional[dict]:
    """
    可选的用户认证，如果没有token则返回None
    
    Args:
        authorization: Authorization header (Bearer token)
        settings: 配置
        
    Returns:
        用户信息字典或None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]
    
    try:
        auth_service = AuthService(settings)
        user = await auth_service.get_user(token)
        user["access_token"] = token
        return user
    except:
        return None
