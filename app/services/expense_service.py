"""
支出服务模块 - Supabase Database
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client
from app.config import Settings


class ExpenseService:
    """支出管理服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def get_expenses_by_plan(
        self, 
        plan_id: str, 
        access_token: str
    ) -> List[Dict[str, Any]]:
        """
        获取行程的所有支出记录
        
        Args:
            plan_id: 行程 ID
            access_token: 访问令牌
            
        Returns:
            支出记录列表
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("expenses")\
                .select("*")\
                .eq("plan_id", plan_id)\
                .order("expense_date", desc=True)\
                .execute()
            
            return response.data if response.data else []
                
        except Exception as e:
            raise Exception(f"获取支出记录失败: {str(e)}")
    
    async def create_expense(
        self, 
        expense_data: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """
        创建支出记录
        
        Args:
            expense_data: 支出数据
            access_token: 访问令牌
            
        Returns:
            创建的支出记录 ID
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("expenses")\
                .insert(expense_data)\
                .execute()
            
            if response.data and len(response.data) > 0:
                return {"id": response.data[0]["id"]}
            else:
                raise Exception("创建支出记录失败")
                
        except Exception as e:
            raise Exception(f"创建支出记录失败: {str(e)}")
    
    async def update_expense(
        self, 
        expense_id: str, 
        expense_data: Dict[str, Any], 
        access_token: str
    ) -> bool:
        """
        更新支出记录
        
        Args:
            expense_id: 支出记录 ID
            expense_data: 更新的数据
            access_token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("expenses")\
                .update(expense_data)\
                .eq("id", expense_id)\
                .execute()
            
            return response.data is not None and len(response.data) > 0
                
        except Exception as e:
            raise Exception(f"更新支出记录失败: {str(e)}")
    
    async def delete_expense(
        self, 
        expense_id: str, 
        access_token: str
    ) -> bool:
        """
        删除支出记录
        
        Args:
            expense_id: 支出记录 ID
            access_token: 访问令牌
            
        Returns:
            是否成功
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            response = self.supabase.table("expenses")\
                .delete()\
                .eq("id", expense_id)\
                .execute()
            
            return True
                
        except Exception as e:
            raise Exception(f"删除支出记录失败: {str(e)}")
    
    async def get_expense_summary(
        self, 
        plan_id: str, 
        access_token: str
    ) -> Dict[str, Any]:
        """
        获取行程的支出汇总
        
        Args:
            plan_id: 行程 ID
            access_token: 访问令牌
            
        Returns:
            支出汇总信息
        """
        try:
            # 设置 token 进行 RLS 认证
            self.supabase.auth.set_session(access_token, access_token)
            
            # 获取所有支出记录
            expenses = await self.get_expenses_by_plan(plan_id, access_token)
            
            # 计算汇总
            total = sum(expense["amount"] for expense in expenses)
            by_category = {}
            
            for expense in expenses:
                category = expense.get("category", "其他")
                by_category[category] = by_category.get(category, 0) + expense["amount"]
            
            return {
                "total": total,
                "count": len(expenses),
                "by_category": by_category
            }
                
        except Exception as e:
            raise Exception(f"获取支出汇总失败: {str(e)}")
