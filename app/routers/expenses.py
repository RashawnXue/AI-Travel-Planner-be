"""
支出相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import date
from app.config import get_settings, Settings
from app.services.expense_service import ExpenseService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class CreateExpenseRequest(BaseModel):
    """创建支出请求"""
    plan_id: str
    category: str
    description: str
    amount: float
    expense_date: str
    expense_time: str


class UpdateExpenseRequest(BaseModel):
    """更新支出请求"""
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    expense_date: Optional[str] = None
    expense_time: Optional[str] = None


class ExpenseResponse(BaseModel):
    """支出响应"""
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None


class ExpensesListResponse(BaseModel):
    """支出列表响应"""
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, str]] = None


@router.get("/plan/{plan_id}", response_model=ExpensesListResponse)
async def get_expenses_by_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    获取行程的所有支出记录
    """
    try:
        expense_service = ExpenseService(settings)
        expenses = await expense_service.get_expenses_by_plan(
            plan_id=plan_id,
            access_token=current_user["access_token"]
        )
        return ExpensesListResponse(data=expenses, error=None)
    except Exception as e:
        return ExpensesListResponse(
            data=None,
            error={"message": str(e)}
        )


@router.get("/plan/{plan_id}/summary", response_model=ExpenseResponse)
async def get_expense_summary(
    plan_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    获取行程的支出汇总
    """
    try:
        expense_service = ExpenseService(settings)
        summary = await expense_service.get_expense_summary(
            plan_id=plan_id,
            access_token=current_user["access_token"]
        )
        return ExpenseResponse(data=summary, error=None)
    except Exception as e:
        return ExpenseResponse(
            data=None,
            error={"message": str(e)}
        )


@router.post("", response_model=ExpenseResponse)
async def create_expense(
    request: CreateExpenseRequest,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    创建支出记录
    """
    try:
        expense_service = ExpenseService(settings)
        
        # 构建支出数据
        expense_data = {
            "user_id": current_user["id"],
            "plan_id": request.plan_id,
            "category": request.category,
            "description": request.description,
            "amount": request.amount,
            "expense_date": request.expense_date,
            "expense_time": request.expense_time
        }
        
        result = await expense_service.create_expense(
            expense_data=expense_data,
            access_token=current_user["access_token"]
        )
        return ExpenseResponse(data=result, error=None)
    except Exception as e:
        return ExpenseResponse(
            data=None,
            error={"message": str(e)}
        )


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    request: UpdateExpenseRequest,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    更新支出记录
    """
    try:
        expense_service = ExpenseService(settings)
        
        # 只更新提供的字段
        update_data = {
            k: v for k, v in request.dict().items() 
            if v is not None
        }
        
        success = await expense_service.update_expense(
            expense_id=expense_id,
            expense_data=update_data,
            access_token=current_user["access_token"]
        )
        
        if success:
            return ExpenseResponse(
                data={"id": expense_id, "updated": True},
                error=None
            )
        else:
            return ExpenseResponse(
                data=None,
                error={"message": "更新失败"}
            )
    except Exception as e:
        return ExpenseResponse(
            data=None,
            error={"message": str(e)}
        )


@router.delete("/{expense_id}", response_model=ExpenseResponse)
async def delete_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    删除支出记录
    """
    try:
        expense_service = ExpenseService(settings)
        success = await expense_service.delete_expense(
            expense_id=expense_id,
            access_token=current_user["access_token"]
        )
        
        if success:
            return ExpenseResponse(
                data={"id": expense_id, "deleted": True},
                error=None
            )
        else:
            return ExpenseResponse(
                data=None,
                error={"message": "删除失败"}
            )
    except Exception as e:
        return ExpenseResponse(
            data=None,
            error={"message": str(e)}
        )
