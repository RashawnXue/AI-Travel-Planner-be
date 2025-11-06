"""
ASR 语音识别服务模块
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from app.config import Settings


class ASRService:
    """阿里云百炼语音识别服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.submit_url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
        self.query_url_base = "https://dashscope.aliyuncs.com/api/v1/tasks"
        self.timeout = 30.0
    
    async def submit_task(
        self,
        file_url: str,
        api_key: Optional[str] = None
    ) -> str:
        """
        提交语音识别任务
        
        Args:
            file_url: OSS 上的音频文件 URL
            api_key: API 密钥（可选）
            
        Returns:
            任务 ID
        """
        key = api_key or self.settings.bailian_api_key
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
            "X-DashScope-OssResourceResolve": "enable"
        }
        
        payload = {
            "model": "paraformer-v2",
            "input": {
                "file_urls": [file_url]
            },
            "parameters": {
                "language_hints": ["zh", "en"]
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.submit_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                return result["output"]["task_id"]
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else {}
                error_message = error_data.get("message") or "提交识别任务失败"
                raise Exception(error_message)
            except Exception as e:
                raise Exception(f"提交识别任务异常: {str(e)}")
    
    async def query_task(
        self,
        task_id: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询任务状态和结果
        
        Args:
            task_id: 任务 ID
            api_key: API 密钥（可选）
            
        Returns:
            任务信息
        """
        key = api_key or self.settings.bailian_api_key
        
        headers = {
            "Authorization": f"Bearer {key}"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.query_url_base}/{task_id}", headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else {}
                error_message = error_data.get("message") or "查询任务失败"
                raise Exception(error_message)
            except Exception as e:
                raise Exception(f"查询任务异常: {str(e)}")
    
    async def get_transcription_text(self, transcription_url: str) -> str:
        """
        获取识别结果文本
        
        Args:
            transcription_url: 识别结果 URL
            
        Returns:
            识别的文本内容
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(transcription_url)
                response.raise_for_status()
                result = response.json()
                
                # 从 transcripts 中提取文本
                text = "\n".join([t["text"] for t in result.get("transcripts", [])])
                return text
            except Exception as e:
                raise Exception(f"获取识别结果失败: {str(e)}")
    
    async def recognize_with_polling(
        self,
        file_url: str,
        api_key: Optional[str] = None,
        max_retries: int = 60,
        interval: float = 2.0
    ) -> str:
        """
        提交任务并轮询直到完成
        
        Args:
            file_url: 音频文件 URL
            api_key: API 密钥
            max_retries: 最大轮询次数
            interval: 轮询间隔（秒）
            
        Returns:
            识别的文本
        """
        # 提交任务
        task_id = await self.submit_task(file_url, api_key)
        
        # 轮询查询状态
        for _ in range(max_retries):
            result = await self.query_task(task_id, api_key)
            
            task_status = result.get("output", {}).get("task_status")
            
            if task_status == "SUCCEEDED":
                # 任务成功，获取识别结果
                results = result.get("output", {}).get("results", [])
                if results and results[0].get("transcription_url"):
                    transcription_url = results[0]["transcription_url"]
                    return await self.get_transcription_text(transcription_url)
                raise Exception("未找到识别结果")
            
            elif task_status == "FAILED":
                # 任务失败
                message = result.get("output", {}).get("results", [{}])[0].get("message", "识别任务失败")
                raise Exception(message)
            
            # 继续等待
            await asyncio.sleep(interval)
        
        raise Exception("识别任务超时")
