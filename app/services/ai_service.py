"""
AI 服务模块 - 阿里云百炼
"""
import httpx
from typing import Dict, Any, Optional
from app.config import Settings


class AIService:
    """阿里云百炼 AI 服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/apps"
        self.timeout = 300.0  # 5 分钟超时
    
    async def invoke_completion(
        self,
        prompt: str,
        api_key: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        debug: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        调用百炼 App 的 completion 能力
        
        Args:
            prompt: 用户输入的提示词
            api_key: API 密钥（可选，如果不提供则使用配置中的）
            parameters: 调用参数（可选）
            debug: 调试参数（可选）
            
        Returns:
            API 响应数据
        """
        # 使用传入的 API Key 或配置中的 Key
        key = api_key or self.settings.bailian_api_key
        
        endpoint = f"{self.base_url}/{self.settings.bailian_app_id}/completion"
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {"prompt": prompt},
            "parameters": parameters or {},
            "debug": debug or {}
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise Exception("AI 生成超时（超过5分钟），请稍后重试或简化需求")
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else {}
                error_message = error_data.get("message") or error_data.get("error") or "调用百炼接口失败"
                raise Exception(error_message)
            except Exception as e:
                raise Exception(f"请求百炼接口异常: {str(e)}")
    
    @staticmethod
    def extract_text(response: Dict[str, Any]) -> str:
        """
        从百炼 API 响应中提取文本内容
        
        Args:
            response: API 响应数据
            
        Returns:
            提取的文本内容
        """
        print(f"Extracting text from response: {response}")
        # 阿里云百炼标准返回格式: {"output": {"text": "实际内容"}}
        if "output" in response and "text" in response["output"]:
            return response["output"]["text"]
        
        # 兼容其他可能的格式
        if "text" in response:
            return response["text"]
        
        # 如果都不存在，返回空字符串
        return ""
