# -*- coding: utf-8 -*-
"""
Chat 对话相关的 API 路由
"""
from fastapi import APIRouter, HTTPException

from ..models.chat_models import ChatRequest, ChatResponse
from ..services.chat_service import call_chat_api

router = APIRouter(prefix="/chat")


@router.post("/", response_model=ChatResponse, summary="大模型对话接口")
async def chat(request: ChatRequest):
    """
    与大模型进行对话，基于表结构信息回答用户问题

    - **table_info**: 表结构信息字符串（可以是建表语句或表描述）
    - **question**: 用户的问题
    - **model_name**: 使用的模型名称（可选，不指定则使用默认模型）

    返回模型的回答
    """
    try:
        answer = call_chat_api(
            table_info=request.table_info,
            question=request.question,
            model_name=request.model_name
        )

        return ChatResponse(
            success=True,
            answer=answer,
            model_name=request.model_name
        )
    except HTTPException as e:
        return ChatResponse(
            success=False,
            error=str(e.detail)
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            error=f"Chat 调用失败: {str(e)}"
        )
