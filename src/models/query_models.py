# -*- coding: utf-8 -*-
"""
SQL 查询相关的请求/响应模型
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    query: str
    table_name: Optional[str] = None
    table_names: Optional[List[str]] = None
    model_name: Optional[str] = None


class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    total_rows: Optional[int] = None
    error: Optional[str] = None
    model_response: Optional[str] = None


class TablesResponse(BaseModel):
    success: bool
    tables: List[str]
    count: int


class ModelsResponse(BaseModel):
    success: bool
    models: Dict[str, Dict[str, Any]]
    default_model: Optional[str] = None
