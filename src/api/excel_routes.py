# -*- coding: utf-8 -*-
"""
Excel 导入相关的 API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import shutil
import time
from ..models.excel_models import (
    ExcelImportRequest,
    ExcelImportResponse,
    ExcelSheetsRequest,
    ExcelSheetsResponse,
    ConfigUpdateRequest,
    ConfigUpdateResponse,
    BatchImportRequest,
    BatchImportResponse,
    BatchImportResult
)
from ..services.excel_service import ExcelImportService

router = APIRouter(prefix="/excel")

# 文件上传目录
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/import", response_model=ExcelImportResponse, summary="导入 Excel 文件到数据库")
async def import_excel(request: ExcelImportRequest):
    """
    将 Excel 文件导入到 SQLite 数据库

    - **excel_path**: Excel 文件的绝对路径
    - **sheet_name**: 要导入的 Sheet 名称
    - **table_name**: 目标数据库表名
    - **if_exists**: 表存在时的处理方式 (fail/replace/append)
    """
    try:
        result = ExcelImportService.import_excel(
            excel_path=request.excel_path,
            sheet_name=request.sheet_name,
            table_name=request.table_name,
            if_exists=request.if_exists
        )
        return ExcelImportResponse(success=True, **result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return ExcelImportResponse(success=False, error=str(e))


@router.post("/sheets", response_model=ExcelSheetsResponse, summary="获取 Excel 文件的所有 Sheet")
async def get_excel_sheets(request: ExcelSheetsRequest):
    """
    获取 Excel 文件中的所有 Sheet 名称

    - **excel_path**: Excel 文件的绝对路径
    """
    try:
        sheets = ExcelImportService.get_sheets(request.excel_path)
        return ExcelSheetsResponse(
            success=True,
            sheets=sheets,
            count=len(sheets)
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return ExcelSheetsResponse(success=False, error=str(e))


@router.post("/update_config", response_model=ConfigUpdateResponse, summary="更新数据库配置文件")
async def update_config(request: ConfigUpdateRequest):
    """
    扫描数据库并更新配置文件

    - **mode**: 更新模式
      - `add`: 仅添加新表，保留已有配置
      - `replace`: 完全重新生成配置文件
    """
    try:
        result = ExcelImportService.update_config(mode=request.mode)
        return ConfigUpdateResponse(success=True, **result)
    except Exception as e:
        return ConfigUpdateResponse(success=False, error=str(e))


@router.post("/batch_import", response_model=BatchImportResponse, summary="批量导入 Excel 文件")
async def batch_import(request: BatchImportRequest):
    """
    批量导入多个 Excel 文件到数据库

    - **configs**: 导入配置列表，每项包含 excel_path, sheet_name, table_name
    - **if_exists**: 表存在时的处理方式
    - **auto_update_config**: 是否在导入成功后自动更新配置文件
    """
    try:
        configs = [cfg.dict() for cfg in request.configs]
        result = ExcelImportService.batch_import(
            configs=configs,
            if_exists=request.if_exists,
            auto_update_config=request.auto_update_config
        )

        return BatchImportResponse(
            success=result["succeeded"] > 0,
            total=result["total"],
            succeeded=result["succeeded"],
            failed=result["failed"],
            results=[BatchImportResult(**r) for r in result["results"]],
            config_updated=result.get("config_updated")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", summary="上传 Excel 文件")
async def upload_excel(file: UploadFile = File(...)):
    """
    上传 Excel 文件到服务器

    返回上传后的文件路径
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="仅支持 .xlsx 或 .xls 文件")

        # 生成唯一文件名
        timestamp = int(time.time() * 1000)
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename,
            "saved_filename": saved_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
