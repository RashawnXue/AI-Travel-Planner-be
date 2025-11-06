"""
ASR 语音识别 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.config import get_settings, Settings
from app.services.asr_service import ASRService
from app.services.oss_service import OSSService

router = APIRouter(prefix="/asr", tags=["ASR"])


class RecognizeRequest(BaseModel):
    """识别请求（已有 OSS URL）"""
    file_url: str
    api_key: Optional[str] = None


class RecognizeResponse(BaseModel):
    """识别响应"""
    text: str


@router.post("/recognize-url", response_model=RecognizeResponse)
async def recognize_from_url(
    request: RecognizeRequest,
    settings: Settings = Depends(get_settings)
):
    """
    识别已上传到 OSS 的音频文件
    
    Args:
        file_url: OSS 文件 URL
        api_key: API 密钥（可选）
    
    Returns:
        识别的文本
    """
    try:
        asr_service = ASRService(settings)
        text = await asr_service.recognize_with_polling(
            file_url=request.file_url,
            api_key=request.api_key
        )
        return RecognizeResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_audio(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings)
):
    """
    上传并识别音频文件（一步完成）
    
    Args:
        file: 音频文件
        api_key: API 密钥（从 FormData 获取，可选）
    
    Returns:
        识别的文本
    """
    file_url = None
    try:
        # 1. 上传到 OSS
        content = await file.read()
        file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "wav"
        
        oss_service = OSSService(settings)
        file_url = await oss_service.upload_audio(content, file_extension)
        
        # 2. 提交识别任务并轮询
        asr_service = ASRService(settings)
        text = await asr_service.recognize_with_polling(
            file_url=file_url,
            api_key=api_key
        )
        
        # 3. 删除临时文件
        await oss_service.delete_file(file_url)
        
        return RecognizeResponse(text=text)
    except Exception as e:
        # 如果失败，尝试清理 OSS 文件
        if file_url:
            try:
                oss_service = OSSService(settings)
                await oss_service.delete_file(file_url)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))
