# -*- coding: utf-8 -*-
"""
查询相关的 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List

from ..models import QueryRequest, QueryResponse, TablesResponse, ModelsResponse
from ..services import call_model_api, execute_sql, DatabaseService
from ..utils import extract_sql, fix_table_name, save_query_log
from ..config import get_db_config, get_model_config

router = APIRouter()


@router.get("/tables", response_model=TablesResponse, summary="获取可用表列表")
async def get_tables():
    db_config = get_db_config()
    if db_config is None:
        raise HTTPException(status_code=500, detail="数据库配置未加载")
    tables = list(db_config.keys())
    return TablesResponse(success=True, tables=tables, count=len(tables))


@router.get("/tables/{table_name}/schema", summary="获取表结构")
async def get_table_schema(table_name: str):
    schema = DatabaseService.get_table_schema(table_name)
    if not schema:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")
    return schema


@router.get("/models", response_model=ModelsResponse, summary="获取可用模型列表")
async def get_models():
    model_config = get_model_config()
    if model_config is None:
        raise HTTPException(status_code=500, detail="模型配置未加载")
    enabled_models = {name: info for name, info in model_config["models"].items() if info.get("enabled", True)}
    return ModelsResponse(
        success=True,
        models=enabled_models,
        default_model=model_config.get("default_model"),
    )


@router.post("/query", response_model=QueryResponse, summary="执行SQL查询")
async def query_data(request: QueryRequest):
    """根据自然语言查询生成并执行SQL"""
    db_config = get_db_config()
    if db_config is None:
        raise HTTPException(status_code=500, detail="数据库配置未加载")

    table_names = []
    if request.table_names:
        table_names = request.table_names
        for table_name in table_names:
            if table_name not in db_config:
                raise HTTPException(status_code=400, detail=f"表 '{table_name}' 不存在")
    elif request.table_name:
        if request.table_name not in db_config:
            raise HTTPException(status_code=400, detail=f"表 '{request.table_name}' 不存在")
        table_names = [request.table_name]
    else:
        raise HTTPException(status_code=400, detail="必须指定table_name或table_names")

    query_text = request.query
    model_name = request.model_name
    model_response = ""
    sql = ""
    log_type = 0

    try:
        model_response = call_model_api(query_text, table_names, model_name)
        print(f"[INFO] 模型请求成功 {model_response}")
        sql = extract_sql(model_response)
        print(f"[INFO] 提取SQL成功 {sql}")
        if sql == model_response.strip():
            save_query_log(
                {
                    "query": query_text,
                    "tables": table_names,
                    "llm_res": model_response,
                    "sql": "",
                    "type": 0,
                }
            )
            return QueryResponse(
                success=False,
                error="无法从模型响应中提取SQL语句",
                model_response=model_response,
            )

        sql = fix_table_name(sql, table_names)

        # 执行 SQL
        try:
            result = execute_sql(sql)
            total_rows = result.get("total_rows", 0)
            if total_rows > 0:
                log_type = 3
            else:
                log_type = 2
        except Exception:
            log_type = 1
            raise

        save_query_log(
            {
                "query": query_text,
                "tables": table_names,
                "llm_res": model_response,
                "sql": sql,
                "type": log_type,
            }
        )

        return QueryResponse(
            success=True,
            sql=sql,
            data=result["data"],
            columns=result["columns"],
            total_rows=result["total_rows"],
            model_response=model_response,
        )

    except Exception as e:
        if log_type == 0:
            save_query_log(
                {
                    "query": query_text,
                    "tables": table_names,
                    "llm_res": model_response,
                    "sql": sql,
                    "type": 1 if sql else 0,
                }
            )
        error_message = str(e.detail) if isinstance(e, HTTPException) else str(e)
        return QueryResponse(success=False, error=error_message)


@router.post("/execute_raw_sql", summary="直接执行自定义SQL")
async def execute_raw_sql(request: Dict[str, str]):
    sql = request.get("sql")
    try:
        result = execute_sql(sql)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/table_preview/{table_name}", summary="预览表数据")
async def preview_table(table_name: str, limit: int = 50):
    sql = f"SELECT * FROM {table_name} LIMIT {limit}"
    try:
        result = execute_sql(sql)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/tables/{table_name}", summary="删除表")
async def delete_table(table_name: str):
    """删除指定的数据库表"""
    from ..services.excel_service import ExcelImportService
    from ..config import DB_PATH
    import sqlite3

    try:
        # 直接使用可写连接执行 DROP TABLE
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            conn.commit()
        finally:
            conn.close()

        # 自动更新配置文件并重载
        try:
            ExcelImportService.update_config(mode="replace")
            return {
                "success": True,
                "message": f"表 '{table_name}' 已成功删除，配置已更新"
            }
        except Exception as config_err:
            return {
                "success": True,
                "message": f"表 '{table_name}' 已删除，但配置更新失败: {str(config_err)}"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除表失败: {str(e)}")
