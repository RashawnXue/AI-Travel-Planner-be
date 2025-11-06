"""
OSS 服务模块
"""
import oss2
import uuid
from datetime import datetime
from app.config import Settings


class OSSService:
    """阿里云 OSS 服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
        endpoint = f"https://{settings.oss_region}.aliyuncs.com"
        self.bucket = oss2.Bucket(auth, endpoint, settings.oss_bucket)
    
    async def upload_audio(self, file_content: bytes, file_extension: str = "wav") -> str:
        """
        上传音频文件到 OSS
        
        Args:
            file_content: 文件内容
            file_extension: 文件扩展名
            
        Returns:
            文件的公网 URL
        """
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        object_name = f"audio/{timestamp}_{unique_id}.{file_extension}"
        
        # 上传文件
        self.bucket.put_object(object_name, file_content)
        
        # 返回公网 URL
        return f"https://{self.settings.oss_bucket}.{self.settings.oss_region}.aliyuncs.com/{object_name}"
    
    async def delete_file(self, file_url: str) -> bool:
        """
        从 OSS 删除文件
        
        Args:
            file_url: 文件的完整 URL
            
        Returns:
            是否删除成功
        """
        try:
            # 从 URL 中提取 object_name
            object_name = file_url.split(f"{self.settings.oss_bucket}.{self.settings.oss_region}.aliyuncs.com/")[-1]
            self.bucket.delete_object(object_name)
            return True
        except Exception as e:
            print(f"删除 OSS 文件失败: {e}")
            return False
