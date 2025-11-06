"""
行程相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.config import get_settings, Settings
from app.services.plan_service import PlanService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/plans", tags=["Plans"])


class CreatePlanRequest(BaseModel):
    """创建行程请求"""
    title: str
    destination: str
    days: int
    budget: float
    travelers: int
    preferences: List[str]
    start_date: str
    summary: str
    ai_response: Dict[str, Any]


class UpdatePlanRequest(BaseModel):
    """更新行程请求"""
    title: Optional[str] = None
    destination: Optional[str] = None
    days: Optional[int] = None
    budget: Optional[float] = None
    travelers: Optional[int] = None
    preferences: Optional[List[str]] = None
    start_date: Optional[str] = None
    summary: Optional[str] = None
    ai_response: Optional[Dict[str, Any]] = None


class PlanResponse(BaseModel):
    """行程响应"""
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None


class PlansListResponse(BaseModel):
    """行程列表响应"""
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, str]] = None


@router.get("", response_model=PlansListResponse)
async def get_plans(
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    获取当前用户的所有行程
    """
    try:
        plan_service = PlanService(settings)
        plans = await plan_service.get_plans_by_user(
            user_id=current_user["id"],
            access_token=current_user["access_token"]
        )
        return PlansListResponse(data=plans, error=None)
    except Exception as e:
        return PlansListResponse(
            data=None,
            error={"message": str(e)}
        )


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    根据 ID 获取行程详情
    """
    try:
        plan_service = PlanService(settings)
        plan = await plan_service.get_plan_by_id(
            plan_id=plan_id,
            access_token=current_user["access_token"]
        )
        return PlanResponse(data=plan, error=None)
    except Exception as e:
        return PlanResponse(
            data=None,
            error={"message": str(e)}
        )


@router.post("", response_model=PlanResponse)
async def create_plan(
    request: CreatePlanRequest,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    创建新行程
    """
    try:
        plan_service = PlanService(settings)
        
        # 从大模型响应中提取文本内容
        ai_text = None
        if request.ai_response:
            # 阿里云百炼返回格式: {"output": {"text": "实际内容"}}
            ai_text = request.ai_response.get("output", {}).get("text")
            if not ai_text:
                # 兼容其他可能的格式
                ai_text = request.ai_response.get("text") or str(request.ai_response)
        
        # 构建行程数据
        plan_data = {
            "user_id": current_user["id"],
            "title": request.title,
            "destination": request.destination,
            "days": request.days,
            "budget": request.budget,
            "travelers": request.travelers,
            "preferences": request.preferences,
            "start_date": request.start_date,
            "summary": request.summary,
            "ai_response": ai_text  # 只存储提取的文本
        }
        
        result = await plan_service.create_plan(
            plan_data=plan_data,
            access_token=current_user["access_token"]
        )
        return PlanResponse(data=result, error=None)
    except Exception as e:
        return PlanResponse(
            data=None,
            error={"message": str(e)}
        )


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    request: UpdatePlanRequest,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    更新行程
    """
    try:
        plan_service = PlanService(settings)
        
        # 只更新提供的字段
        update_data = {
            k: v for k, v in request.dict().items() 
            if v is not None
        }
        
        # 如果更新了 ai_response，提取其中的文本
        if "ai_response" in update_data and update_data["ai_response"]:
            ai_response = update_data["ai_response"]
            # 阿里云百炼返回格式: {"output": {"text": "实际内容"}}
            ai_text = ai_response.get("output", {}).get("text")
            if not ai_text:
                # 兼容其他可能的格式
                ai_text = ai_response.get("text") or str(ai_response)
            update_data["ai_response"] = ai_text
        
        success = await plan_service.update_plan(
            plan_id=plan_id,
            plan_data=update_data,
            access_token=current_user["access_token"]
        )
        
        if success:
            return PlanResponse(
                data={"id": plan_id, "updated": True},
                error=None
            )
        else:
            return PlanResponse(
                data=None,
                error={"message": "更新失败"}
            )
    except Exception as e:
        return PlanResponse(
            data=None,
            error={"message": str(e)}
        )


@router.delete("/{plan_id}", response_model=PlanResponse)
async def delete_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    删除行程
    """
    try:
        plan_service = PlanService(settings)
        success = await plan_service.delete_plan(
            plan_id=plan_id,
            access_token=current_user["access_token"]
        )
        
        if success:
            return PlanResponse(
                data={"id": plan_id, "deleted": True},
                error=None
            )
        else:
            return PlanResponse(
                data=None,
                error={"message": "删除失败"}
            )
    except Exception as e:
        return PlanResponse(
            data=None,
            error={"message": str(e)}
        )
