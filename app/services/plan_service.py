"""
行程服务模块 - Supabase Database
"""
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from app.config import Settings


class PlanService:
    """行程管理服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def get_plans_by_user(
        self, 
        user_id: str, 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有行程
        
        Args:
            user_id: 用户 ID
            access_token: 访问令牌
            
        Returns:
            行程列表
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("travel_plans")\
                .select("id, title, destination, days, budget, start_date, created_at")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
                
        except Exception as e:
            raise Exception(f"获取行程列表失败: {str(e)}")
    
    async def get_plan_by_id(
        self, 
        plan_id: str, 
        access_token: str
    ) -> Dict[str, Any]:
        """
        根据 ID 获取行程详情
        
        Args:
            plan_id: 行程 ID
            access_token: 访问令牌
            
        Returns:
            行程详情
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("travel_plans")\
                .select("*")\
                .eq("id", plan_id)\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            else:
                raise Exception("行程不存在")
                
        except Exception as e:
            raise Exception(f"获取行程详情失败: {str(e)}")
    
    async def create_plan(
        self, 
        plan_data: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """
        创建新行程
        
        Args:
            plan_data: 行程数据
            access_token: 访问令牌
            
        Returns:
            创建的行程 ID
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("travel_plans")\
                .insert(plan_data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return {"id": response.data[0]["id"]}
            else:
                raise Exception("创建行程失败")
                
        except Exception as e:
            raise Exception(f"创建行程失败: {str(e)}")
    
    async def update_plan(
        self, 
        plan_id: str, 
        plan_data: Dict[str, Any], 
        access_token: str
    ) -> bool:
        """
        更新行程
        
        Args:
            plan_id: 行程 ID
            plan_data: 更新的数据
            access_token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("travel_plans")\
                .update(plan_data)\
                .eq("id", plan_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
                
        except Exception as e:
            raise Exception(f"更新行程失败: {str(e)}")
    
    async def delete_plan(
        self, 
        plan_id: str, 
        access_token: str
    ) -> bool:
        """
        删除行程
        
        Args:
            plan_id: 行程 ID
            access_token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("travel_plans")\
                .delete()\
                .eq("id", plan_id)\
                .execute()
            
            return True
                
        except Exception as e:
            raise Exception(f"删除行程失败: {str(e)}")
