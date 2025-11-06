"""
缓存使用示例

以下示例展示如何在服务中使用缓存来提升性能。
注意：缓存适用于不经常变化的数据，对于实时数据请谨慎使用。
"""

from app.utils.cache import cached
from app.services.plan_service import PlanService

# 示例 1：缓存用户行程列表（缓存 60 秒）
# 适用场景：用户短时间内多次刷新行程列表

class CachedPlanService(PlanService):
    """带缓存的行程服务（可选使用）"""
    
    @cached(ttl_seconds=60)  # 缓存 1 分钟
    async def get_plans_by_user_cached(
        self, 
        user_id: str, 
        access_token: str
    ):
        """获取用户行程（带缓存）"""
        return await self.get_plans_by_user(user_id, access_token)


# 示例 2：在路由中使用缓存

"""
from app.utils.cache import cached

@router.get("/stats/summary")
@cached(ttl_seconds=300)  # 缓存 5 分钟
async def get_summary_stats(
    current_user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    # 统计数据不需要实时更新，可以缓存
    expense_service = ExpenseService(settings)
    summary = await expense_service.get_expense_summary(...)
    return summary
"""

# 示例 3：手动清除缓存

"""
from app.utils.cache import clear_cache

@router.post("/plans")
async def create_plan(...):
    # 创建行程
    result = await plan_service.create_plan(...)
    
    # 清除缓存，确保下次获取最新数据
    clear_cache()
    
    return result
"""

# 注意事项：
# 1. 不要缓存包含敏感信息的数据
# 2. 不要缓存频繁变化的数据
# 3. 写操作后考虑清除相关缓存
# 4. 根据业务需求调整 TTL（缓存有效期）
