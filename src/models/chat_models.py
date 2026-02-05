# -*- coding: utf-8 -*-
"""
Chat 对话相关的请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Chat 对话请求"""
    table_info: str = Field(..., description="表结构信息字符串")
    question: str = Field(..., description="用户问题")
    model_name: Optional[str] = Field(None, description="使用的模型名称，不指定则使用默认模型")


class ChatResponse(BaseModel):
    """Chat 对话响应"""
    success: bool
    answer: Optional[str] = None
    model_name: Optional[str] = None
    error: Optional[str] = None
