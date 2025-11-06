"""
OSS 相关 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from app.config import get_settings, Settings
from app.services.oss_service import OSSService

router = APIRouter(prefix="/oss", tags=["OSS"])


class UploadResponse(BaseModel):
    """上传响应"""
    file_url: str


class DeleteRequest(BaseModel):
    """删除请求"""
    file_url: str


class DeleteResponse(BaseModel):
    """删除响应"""
    success: bool


@router.post("/upload/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    上传音频文件到 OSS
    
    用于语音识别前的文件上传
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 获取文件扩展名
        file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "wav"
        
        # 上传到 OSS
        oss_service = OSSService(settings)
        file_url = await oss_service.upload_audio(content, file_extension)
        
        return UploadResponse(file_url=file_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@router.post("/delete", response_model=DeleteResponse)
async def delete_file(
    request: DeleteRequest,
    settings: Settings = Depends(get_settings)
):
    """
    从 OSS 删除文件
    """
    try:
        oss_service = OSSService(settings)
        success = await oss_service.delete_file(request.file_url)
        return DeleteResponse(success=success)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")
