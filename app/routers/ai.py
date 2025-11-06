"""
AI 相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta
from app.config import get_settings, Settings
from app.services.ai_service import AIService
from app.services.plan_service import PlanService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])


class CompletionRequest(BaseModel):
    """completion 请求"""
    prompt: str
    api_key: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    debug: Optional[Dict[str, Any]] = None
    extract_text: bool = True  # 是否只返回提取的文本


class CompletionResponse(BaseModel):
    """completion 响应"""
    data: Optional[Dict[str, Any]] = None
    text: Optional[Any] = None  # 提取的文本或解析后的 JSON 对象（当 extract_text=True 时）
    error: Optional[Dict[str, Any]] = None


@router.post("/completion", response_model=CompletionResponse)
async def invoke_completion(
    request: CompletionRequest,
    settings: Settings = Depends(get_settings)
):
    """
    调用百炼 App 的 completion 能力
    
    用于 AI 生成旅行规划
    """
    try:
        ai_service = AIService(settings)
        data = await ai_service.invoke_completion(
            prompt=request.prompt,
            api_key=request.api_key,
            parameters=request.parameters,
            debug=request.debug
        )
        
        # 如果需要提取文本
        extracted_text = None
        if request.extract_text:
            text_content = AIService.extract_text(data)
            # 尝试将 JSON 字符串解析为字典
            try:
                extracted_text = json.loads(text_content)
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的 JSON，保持原始文本
                extracted_text = text_content
            
        
        if extracted_text:
            print(f"Extracted Text: {extracted_text}")
        
        return CompletionResponse(
            data=data, 
            text=extracted_text,
            error=None
        )
    except Exception as e:
        return CompletionResponse(
            data=None,
            text=None,
            error={"message": str(e)}
        )


class GeneratePlanRequest(BaseModel):
    """生成行程请求"""
    prompt: str
    api_key: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class GeneratePlanResponse(BaseModel):
    """生成行程响应"""
    plan_id: Optional[str] = None
    error: Optional[Dict[str, Any]] = None


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_and_create_plan(
    request: GeneratePlanRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """
    调用 AI 生成行程并直接保存到数据库
    
    这个端点会：
    1. 调用百炼 AI 生成行程
    2. 解析 AI 返回的 JSON
    3. 直接插入数据库
    4. 返回创建的行程 ID
    """
    try:
        # 1. 调用 AI 服务生成行程
        ai_service = AIService(settings)
        ai_response = await ai_service.invoke_completion(
            prompt=request.prompt,
            api_key=request.api_key,
            parameters=request.parameters
        )
        
        # 2. 提取文本并解析 JSON
        text_content = AIService.extract_text(ai_response)
        try:
            ai_data = json.loads(text_content)
        except (json.JSONDecodeError, TypeError) as e:
            raise Exception(f"AI 返回的内容不是有效的 JSON: {str(e)}")
        
        # 3. 构建行程数据
        # 处理出发日期
        start_date = ai_data.get("start_date", "").strip()
        if not start_date:
            # 如果没有出发日期，设置为当前日期后三天
            future_date = datetime.now() + timedelta(days=3)
            start_date = future_date.strftime("%Y-%m-%d")
        
        # 构建插入数据库的数据
        plan_data = {
            "user_id": user["id"],
            "title": ai_data.get("title", "").strip() or "未命名行程",
            "destination": ai_data.get("destination", "").strip() or "未知目的地",
            "days": ai_data.get("days", 1),
            "budget": ai_data.get("budget", 0),
            "travelers": ai_data.get("travelers", 1),
            "preferences": ai_data.get("preferences", []) if isinstance(ai_data.get("preferences"), list) else [],
            "start_date": start_date,
            "summary": ai_data.get("summary", "").strip() or "",
            "ai_response": ai_data  # 保存完整的 AI 响应
        }
        
        print(f"Creating travel plan with data: {plan_data}")
        
        # 4. 调用 PlanService 创建行程
        plan_service = PlanService(settings)
        result = await plan_service.create_plan(
            plan_data=plan_data,
            access_token=user["access_token"]
        )
        
        return GeneratePlanResponse(
            plan_id=result["id"],
            error=None
        )
        
    except Exception as e:
        error_message = str(e)
        print(f"Error generating plan: {error_message}")
        return GeneratePlanResponse(
            plan_id=None,
            error={"message": error_message}
        )
