# -*- coding: utf-8 -*-
"""
配置管理相关的 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ..config import (
    get_model_config,
    save_model_config,
    PROMPT_TEMPLATE_FILE,
    CHAT_TEMPLATE_FILE,
)

router = APIRouter(prefix="/config", tags=["配置管理"])


# ========== 请求/响应模型 ==========
class ModelConfigSaveRequest(BaseModel):
    models: Dict[str, Dict[str, Any]]
    default_model: str = None


class TemplateSaveRequest(BaseModel):
    content: str


# ========== API 端点 ==========
@router.get("/model", summary="获取模型配置")
async def get_model_config_api():
    """获取当前的模型配置"""
    try:
        config = get_model_config()
        if config is None:
            raise HTTPException(status_code=500, detail="模型配置未加载")
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型配置失败: {str(e)}")


@router.post("/model", summary="保存模型配置")
async def save_model_config_api(request: ModelConfigSaveRequest):
    """保存模型配置到文件"""
    try:
        config_data = {
            "models": request.models,
            "default_model": request.default_model
        }
        success = save_model_config(config_data)
        if not success:
            raise HTTPException(status_code=500, detail="保存模型配置失败")
        return {"success": True, "message": "模型配置保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存模型配置失败: {str(e)}")


@router.get("/template/{template_type}", summary="获取模板内容")
async def get_template_api(template_type: str):
    """获取指定类型的模板内容"""
    try:
        if template_type == "chat":
            template_file = CHAT_TEMPLATE_FILE
        elif template_type == "infer":
            template_file = PROMPT_TEMPLATE_FILE
        else:
            raise HTTPException(status_code=400, detail=f"不支持的模板类型: {template_type}")

        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()

        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"模板文件不存在: {template_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取模板失败: {str(e)}")


@router.post("/template/{template_type}", summary="保存模板内容")
async def save_template_api(template_type: str, request: TemplateSaveRequest):
    """保存指定类型的模板内容"""
    try:
        if template_type == "chat":
            template_file = CHAT_TEMPLATE_FILE
        elif template_type == "infer":
            template_file = PROMPT_TEMPLATE_FILE
        else:
            raise HTTPException(status_code=400, detail=f"不支持的模板类型: {template_type}")

        with open(template_file, "w", encoding="utf-8") as f:
            f.write(request.content)

        return {"success": True, "message": f"{template_type} 模板保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存模板失败: {str(e)}")
