"""
认证相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.config import get_settings, Settings
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr
    password: str
    username: str


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class UpdatePasswordRequest(BaseModel):
    """更新密码请求"""
    new_password: str


class RefreshTokenRequest(BaseModel):
    """刷新token请求"""
    refresh_token: str


class AuthResponse(BaseModel):
    """认证响应"""
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None


class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    error: Optional[Dict[str, str]] = None


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    settings: Settings = Depends(get_settings)
):
    """
    用户注册
    """
    try:
        auth_service = AuthService(settings)
        result = await auth_service.sign_up(
            email=request.email,
            password=request.password,
            username=request.username
        )
        return AuthResponse(**result, error=None)
    except Exception as e:
        return AuthResponse(
            user=None,
            session=None,
            error={"message": str(e)}
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    settings: Settings = Depends(get_settings)
):
    """
    用户登录
    """
    try:
        auth_service = AuthService(settings)
        result = await auth_service.sign_in(
            email=request.email,
            password=request.password
        )
        return AuthResponse(**result, error=None)
    except Exception as e:
        error_message = str(e)
        # 提取更友好的错误信息
        if "登录失败:" in error_message:
            error_message = error_message.replace("登录失败: ", "")
        
        return AuthResponse(
            user=None,
            session=None,
            error={"message": error_message}
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    用户登出
    """
    try:
        auth_service = AuthService(settings)
        await auth_service.sign_out(current_user["access_token"])
        return MessageResponse(message="登出成功", error=None)
    except Exception as e:
        return MessageResponse(
            message="",
            error={"message": str(e)}
        )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "username": current_user.get("username", ""),
            "created_at": current_user.get("created_at")
        },
        "error": None
    }


@router.put("/password", response_model=MessageResponse)
async def update_password(
    request: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    更新密码
    """
    try:
        auth_service = AuthService(settings)
        await auth_service.update_password(
            access_token=current_user["access_token"],
            new_password=request.new_password
        )
        return MessageResponse(message="密码更新成功", error=None)
    except Exception as e:
        return MessageResponse(
            message="",
            error={"message": str(e)}
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_session(
    request: RefreshTokenRequest,
    settings: Settings = Depends(get_settings)
):
    """
    刷新 session
    """
    try:
        auth_service = AuthService(settings)
        session = await auth_service.refresh_session(request.refresh_token)
        return AuthResponse(
            user=None,
            session=session,
            error=None
        )
    except Exception as e:
        return AuthResponse(
            user=None,
            session=None,
            error={"message": str(e)}
        )
