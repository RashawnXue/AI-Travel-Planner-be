"""
认证服务模块 - Supabase Auth
"""
from typing import Dict, Any, Optional
from supabase import Client
from app.config import Settings
from app.database import get_supabase_client


class AuthService:
    """Supabase 认证服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        # 使用单例客户端，避免每次创建新连接
        self.supabase: Client = get_supabase_client(settings)
    
    async def sign_up(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            email: 用户邮箱
            password: 密码
            username: 用户名
            
        Returns:
            包含用户信息和 session 的字典
        """
        try:
            # 直接尝试注册，让 Supabase 处理邮箱重复的情况
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    # 将用户名存储到 user_metadata
                    "data": {
                        "username": username
                    }
                }
            })
            
            if response.user and response.session:
                user_id = response.user.id
                user_email = response.user.email
                
                # 尝试插入或更新 user_profiles 表中的用户名
                try:
                    self.supabase.table('user_profiles').upsert({
                        'id': user_id,
                        'username': username
                    }).execute()
                except Exception as profile_error:
                    # 如果插入失败，记录但不中断注册流程
                    print(f"插入用户资料失败: {str(profile_error)}")
                
                return {
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "username": username,
                        "created_at": response.user.created_at
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at
                    }
                }
            else:
                raise Exception("注册失败，未返回用户信息或会话信息，请确认已关闭邮箱验证")
                
        except Exception as e:
            error_msg = str(e)
            # 处理 Supabase 返回的常见错误
            if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
                raise Exception("该邮箱已被注册，请使用其他邮箱或直接登录")
            elif "email" in error_msg.lower() and "invalid" in error_msg.lower():
                raise Exception("邮箱格式不正确")
            elif "password" in error_msg.lower():
                raise Exception("密码不符合要求")
            else:
                raise Exception(f"注册失败: {error_msg}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            email: 用户邮箱
            password: 密码
            
        Returns:
            包含用户信息和 session 的字典
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                user_id = response.user.id
                user_email = response.user.email
                
                # 从 user_profiles 表获取用户名
                username = None
                try:
                    profile_response = self.supabase.table('user_profiles').select('username').eq('id', user_id).single().execute()
                    if profile_response.data:
                        username = profile_response.data.get('username')
                except:
                    pass
                
                # 如果仍然没有用户名，设为 None 或空字符串
                if not username:
                    username = ""
                
                return {
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "username": username,
                        "created_at": response.user.created_at
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_at": response.session.expires_at
                    }
                }
            else:
                raise Exception("登录失败，邮箱或密码错误")
                
        except Exception as e:
            raise Exception(f"登录失败: {str(e)}")
    
    async def sign_out(self, access_token: str) -> bool:
        """
        用户登出
        
        Args:
            access_token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            # 设置 token 后再登出
            self.supabase.auth.set_session(access_token, access_token)
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            raise Exception(f"登出失败: {str(e)}")
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Args:
            access_token: 访问令牌
            
        Returns:
            用户信息
        """
        try:
            # 设置 token
            self.supabase.auth.set_session(access_token, access_token)
            response = self.supabase.auth.get_user()
            
            if response.user:
                user_id = response.user.id
                email = response.user.email
                
                # 从 user_profiles 表获取用户名
                username = None
                try:
                    profile_response = self.supabase.table('user_profiles').select('username').eq('id', user_id).single().execute()
                    if profile_response.data:
                        username = profile_response.data.get('username')
                except:
                    pass
                
                # 如果仍然没有用户名，设为空字符串
                if not username:
                    username = ""
                
                return {
                    "id": user_id,
                    "email": email,
                    "username": username,
                    "created_at": response.user.created_at
                }
            else:
                raise Exception("未找到用户信息")
                
        except Exception as e:
            raise Exception(f"获取用户信息失败: {str(e)}")
    
    async def update_password(
        self, 
        access_token: str, 
        new_password: str
    ) -> bool:
        """
        更新密码
        
        Args:
            access_token: 访问令牌
            new_password: 新密码
            
        Returns:
            是否成功
        """
        try:
            # 设置 token
            self.supabase.auth.set_session(access_token, access_token)
            response = self.supabase.auth.update_user({
                "password": new_password
            })
            
            return response.user is not None
                
        except Exception as e:
            raise Exception(f"更新密码失败: {str(e)}")
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新 session
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的 session 信息
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            else:
                raise Exception("刷新 session 失败")
                
        except Exception as e:
            raise Exception(f"刷新 session 失败: {str(e)}")
