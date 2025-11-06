"""
缓存工具模块 - 简单的内存缓存
"""
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, Callable
import hashlib
import json


class SimpleCache:
    """简单的内存缓存类"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 将参数序列化为字符串
        key_data = {
            'func': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry['expires_at']:
                return entry['value']
            else:
                # 过期，删除
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 60):
        """设置缓存值"""
        self._cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
        }
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
_cache = SimpleCache()


def cached(ttl_seconds: int = 60):
    """
    缓存装饰器
    
    Args:
        ttl_seconds: 缓存有效期（秒）
        
    使用示例:
        @cached(ttl_seconds=300)  # 缓存5分钟
        async def get_data():
            return expensive_operation()
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _cache._make_key(func.__name__, args, kwargs)
            
            # 尝试从缓存获取
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            _cache.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator


def clear_cache():
    """清空所有缓存"""
    _cache.clear()
