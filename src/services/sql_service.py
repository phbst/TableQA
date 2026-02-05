# -*- coding: utf-8 -*-
"""
SQL 相关服务
"""
import time
import sqlite3
import requests
from typing import List, Dict, Any
from fastapi import HTTPException

from ..config import (
    DB_PATH,
    PROMPT_TEMPLATE_FILE,
    TEMPERATURE,
    REQUEST_TIMEOUT,
    get_db_config,
    get_model_config,
)
from ..utils import validate_sql_readonly


def call_model_api(query: str, table_names: List[str] = None, model_name: str = None) -> str:
    """调用大模型接口解析 SQL (同步)"""
    model_config = get_model_config()
    db_config = get_db_config()

    if not model_name:
        model_name = model_config.get("default_model", "SFT-Qwen3-8B")

    if model_name not in model_config["models"]:
        raise HTTPException(status_code=400, detail=f"模型 '{model_name}' 不存在")

    model_info = model_config["models"][model_name]

    if not model_info.get("enabled", True):
        raise HTTPException(status_code=400, detail=f"模型 '{model_name}' 已禁用")

    build_statement = ""
    if table_names and db_config:
        table_builds = []
        for table_name in table_names:
            if table_name in db_config:
                table_builds.append(f"【{table_name}】\n{db_config[table_name]['build']}")
        build_statement = "\n\n".join(table_builds)

    try:
        with open(PROMPT_TEMPLATE_FILE, encoding="utf-8") as f:
            prompt = f.read().format(query=query, build=build_statement)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取prompt模板失败: {e}")

    if model_info["type"] == "local":
        api_url = f"{model_info['url']}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": TEMPERATURE,
        }
    else:
        api_url = f"{model_info['url']}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": model_info["api_key"],
        }
        payload = {
            "model": model_info["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": TEMPERATURE,
        }

    try:
        start = time.time()
        resp = requests.post(api_url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        latency = time.time() - start
        print(f"[INFO] 模型 {model_name} 响应耗时: {latency:.2f}s")
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用模型 {model_name} 失败: {e}")


def execute_sql(sql: str) -> Dict[str, Any]:
    """执行SQL并返回结果 (同步)"""
    if not sql:
        raise HTTPException(status_code=400, detail="SQL语句为空")
    if not validate_sql_readonly(sql):
        raise HTTPException(status_code=400, detail="SQL语句不是只读操作")

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        if sql.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            columns = [c[0] for c in cur.description]
            data = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            return {"data": data, "columns": columns, "total_rows": len(data)}
        else:
            conn.commit()
            return {"data": [], "columns": [], "total_rows": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL执行失败: {e}")
    finally:
        conn.close()
