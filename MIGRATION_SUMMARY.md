# Supabase 迁移到后端总结

## 🎯 概述

已将所有 Supabase 相关逻辑从前端迁移到后端，包括：
1. 用户认证（注册、登录、登出）
2. 行程管理（CRUD）
3. 支出管理（CRUD）

## 📁 后端新增文件

###  1. 依赖和配置
- `requirements.txt` - 添加 `supabase`, `python-jose`, `passlib`
- `.env.example` - 添加 Supabase 配置项
- `app/config.py` - 添加 Supabase URL/Key配置

### 2. 服务层 (Services)
- `app/services/auth_service.py` - 认证服务
  - `sign_up()` - 注册
  - `sign_in()` - 登录
  - `sign_out()` - 登出
  - `get_user()` - 获取用户信息
  - `update_password()` - 更新密码
  - `refresh_session()` - 刷新会话

- `app/services/plan_service.py` - 行程服务
  - `get_plans_by_user()` - 获取用户行程列表
  - `get_plan_by_id()` - 获取行程详情
  - `create_plan()` - 创建行程
  - `update_plan()` - 更新行程
  - `delete_plan()` - 删除行程

- `app/services/expense_service.py` - 支出服务
  - `get_expenses_by_plan()` - 获取行程支出
  - `create_expense()` - 创建支出
  - `update_expense()` - 更新支出
  - `delete_expense()` - 删除支出
  - `get_expense_summary()` - 获取支出汇总

### 3. 依赖和中间件
- `app/dependencies/auth.py` - 认证依赖
  - `get_current_user()` - 获取当前用户（必需）
  - `get_optional_user()` - 可选的用户认证

### 4. 路由层 (Routers)
- `app/routers/auth.py` - 认证路由
  - `POST /auth/register` - 注册
  - `POST /auth/login` - 登录
  - `POST /auth/logout` - 登出
  - `GET /auth/me` - 获取当前用户
  - `PUT /auth/password` - 更新密码
  - `POST /auth/refresh` - 刷新token

- `app/routers/plans.py` - 行程路由
  - `GET /plans` - 获取所有行程
  - `GET /plans/{id}` - 获取行程详情
  - `POST /plans` - 创建行程
  - `PUT /plans/{id}` - 更新行程
  - `DELETE /plans/{id}` - 删除行程

- `app/routers/expenses.py` - 支出路由
  - `GET /expenses/plan/{plan_id}` - 获取行程支出
  - `GET /expenses/plan/{plan_id}/summary` - 获取支出汇总
  - `POST /expenses` - 创建支出
  - `PUT /expenses/{id}` - 更新支出
  - `DELETE /expenses/{id}` - 删除支出

### 5. 主应用
- `main.py` - 注册所有新路由

## 📁 前端修改文件

### 已完成
- `src/api/auth.ts` - ✅ 完全重写
  - 使用 `/api/backend/auth` 端点
  - Token 存储在 localStorage
  - 不再直接使用 Supabase

### 待完成（需要创建新文件）
- `src/api/plan.ts` - ⏳ 待更新
- `src/api/expense.ts` - ⏳ 待更新

## 🔧 环境变量配置

### 后端 (.env)
```bash
# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# 其他配置保持不变...
```

### 前端 (.env)
```bash
# Supabase 配置已不再需要（已移至后端）
# VITE_SUPABASE_URL=...
# VITE_SUPABASE_ANON_KEY=...

# 其他配置保持不变...
```

## 🔐 认证流程变更

### 之前（前端直连 Supabase）
```
前端 → Supabase Auth API → 返回 Session
     → Supabase SDK 管理 token
```

### 现在（后端代理）
```
前端 → 后端 API → Supabase Auth API → 返回 Session
    ← JWT Token ← 后端包装返回
    
Token 存储：localStorage (access_token, refresh_token)
认证头：Authorization: Bearer <token>
```

## 📋 下一步任务

1. ⏳ 更新 `src/api/plan.ts` - 调用后端 API
2. ⏳ 更新 `src/api/expense.ts` - 调用后端 API
3. ⏳ 测试完整流程：
   - 注册/登录
   - 创建行程
   - 管理支出
   - 登出

## 🚀 启动指南

### 1. 后端
```bash
cd AI-Travel-Planner-be
pip install -r requirements.txt
# 配置 .env 文件
uvicorn main:app --reload
```

### 2. 前端
```bash
npm run dev
```

### 3. Nginx 代理（已配置）
```nginx
location /api/backend/ {
    proxy_pass http://localhost:8000/;
    ...
}
```

## ⚠️ 注意事项

1. **Session 管理**：现在使用 localStorage 存储 token，不再依赖 Supabase SDK 的 session 管理
2. **RLS 策略**：后端仍然通过 Supabase SDK 操作数据库，RLS 策略依然有效
3. **Token 刷新**：需要实现 token 自动刷新机制（TODO）
4. **错误处理**：后端统一返回 `{data, error}` 格式

## 🔍 API 对照表

| 功能 | 前端旧API | 前端新API | 后端端点 |
|------|----------|----------|---------|
| 注册 | `supabase.auth.signUp()` | `POST /api/backend/auth/register` | `/auth/register` |
| 登录 | `supabase.auth.signInWithPassword()` | `POST /api/backend/auth/login` | `/auth/login` |
| 登出 | `supabase.auth.signOut()` | `POST /api/backend/auth/logout` | `/auth/logout` |
| 获取会话 | `supabase.auth.getSession()` | `GET /api/backend/auth/me` | `/auth/me` |
| 获取行程 | `supabase.from('travel_plans').select()` | `GET /api/backend/plans` | `/plans` |
| 创建行程 | `supabase.from('travel_plans').insert()` | `POST /api/backend/plans` | `/plans` |
| 获取支出 | `supabase.from('expenses').select()` | `GET /api/backend/expenses/plan/{id}` | `/expenses/plan/{id}` |
| 创建支出 | `supabase.from('expenses').insert()` | `POST /api/backend/expenses` | `/expenses` |
