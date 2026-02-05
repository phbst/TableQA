# -*- coding: utf-8 -*-
"""
健康检查和信息相关的 API 路由
"""
import time
from fastapi import APIRouter

from ..config import get_db_config, get_model_config

router = APIRouter()


@router.get("/", summary="根路径")
async def root():
    return {"message": "SQL查询API服务运行中", "version": "2.0.0"}


@router.get("/health", summary="健康检查")
async def health_check():
    db_config = get_db_config()
    model_config = get_model_config()

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "tables_loaded": len(db_config) if db_config else 0,
        "models_loaded": len(model_config["models"]) if model_config else 0,
        "default_model": model_config.get("default_model") if model_config else None,
    }
