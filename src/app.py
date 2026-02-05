# -*- coding: utf-8 -*-
"""
FastAPI 应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import load_db_config, load_model_config
from .api import query_router, health_router, excel_router, chat_router

# 创建 FastAPI 应用
app = FastAPI(
    title="SQL查询API",
    description="支持多表选择问答的SQL查询服务"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 1. 加载配置
    if not load_db_config():
        raise RuntimeError("无法加载数据库配置")
    if not load_model_config():
        raise RuntimeError("无法加载模型配置")

    print("[INFO] ✅ Application startup completed successfully.")


# 注册路由
app.include_router(health_router, tags=["健康检查"])
app.include_router(query_router, tags=["查询"])
app.include_router(chat_router, tags=["对话"])
app.include_router(excel_router, tags=["Excel导入"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
