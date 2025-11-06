"""
认证服务模块 - Supabase Auth
"""
from typing import Dict, Any, Optional
from supabase import create_client, Client
from app.config import Settings


class AuthService:
    """Supabase 认证服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """
        用户注册
        
        Args:
            email: 用户邮箱
            password: 密码
            
        Returns:
            包含用户信息和 session 的字典
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
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
                
                # 如果没有用户名，使用邮箱前缀作为备用
                if not username:
                    username = user_email.split('@')[0] if user_email else None
                
                return {
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "username": username,
                        "created_at": response.user.created_at
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None,
                        "expires_at": response.session.expires_at if response.session else None
                    } if response.session else None
                }
            else:
                raise Exception("注册失败，未返回用户信息")
                
        except Exception as e:
            raise Exception(f"注册失败: {str(e)}")
    
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
                
                # 如果没有用户名，使用邮箱前缀作为备用
                if not username:
                    username = user_email.split('@')[0] if user_email else None
                
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
                profile_response = self.supabase.table('user_profiles').select('username').eq('id', user_id).single().execute()
                
                username = None
                if profile_response.data:
                    username = profile_response.data.get('username')
                
                # 如果没有用户名，使用邮箱前缀作为备用
                if not username:
                    username = email.split('@')[0] if email else None
                
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
