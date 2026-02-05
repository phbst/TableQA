# -*- coding: utf-8 -*-
"""
Excel 导入相关的请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ExcelImportRequest(BaseModel):
    """Excel 导入请求"""
    excel_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="Sheet 名称")
    table_name: str = Field(..., description="目标表名")
    if_exists: str = Field(default="replace", description="表存在时的处理方式: fail/replace/append")


class ExcelImportResponse(BaseModel):
    """Excel 导入响应"""
    success: bool
    table_name: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    original_columns: Optional[List[str]] = None
    normalized_columns: Optional[List[str]] = None
    create_statement: Optional[str] = None
    error: Optional[str] = None


class ExcelSheetsRequest(BaseModel):
    """获取 Excel Sheets 请求"""
    excel_path: str = Field(..., description="Excel 文件路径")


class ExcelSheetsResponse(BaseModel):
    """获取 Excel Sheets 响应"""
    success: bool
    sheets: Optional[List[str]] = None
    count: Optional[int] = None
    error: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    """更新配置文件请求"""
    mode: str = Field(default="add", description="更新模式: add/replace")


class ConfigUpdateResponse(BaseModel):
    """更新配置文件响应"""
    success: bool
    total_tables: Optional[int] = None
    new_tables: Optional[List[str]] = None
    updated_tables: Optional[List[str]] = None
    mode: Optional[str] = None
    config_path: Optional[str] = None
    error: Optional[str] = None


class BatchImportConfig(BaseModel):
    """批量导入配置项"""
    excel_path: str
    sheet_name: str
    table_name: str


class BatchImportRequest(BaseModel):
    """批量导入请求"""
    configs: List[BatchImportConfig] = Field(..., description="批量导入配置列表")
    if_exists: str = Field(default="replace", description="表存在时的处理方式")
    auto_update_config: bool = Field(default=True, description="是否自动更新配置文件")


class BatchImportResult(BaseModel):
    """单个导入结果"""
    table_name: str
    success: bool
    row_count: Optional[int] = None
    error: Optional[str] = None


class BatchImportResponse(BaseModel):
    """批量导入响应"""
    success: bool
    total: int
    succeeded: int
    failed: int
    results: List[BatchImportResult]
    config_updated: Optional[bool] = None
