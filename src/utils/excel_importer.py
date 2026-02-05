# -*- coding: utf-8 -*-
"""
Excel 导入工具模块
提供 Excel 文件导入到 SQLite 数据库的功能
"""
import pandas as pd
import sqlite3
import os
import json
import random
from typing import Dict, Any


def normalize_column_name(col_name: str) -> str:
    """
    标准化列名：去除特殊字符，替换为下划线

    Args:
        col_name: 原始列名

    Returns:
        标准化后的列名
    """
    name = col_name.replace("(", "_").replace(")", "_").replace("（", "_").replace("）", "_")
    name = name.replace("\n", "_").replace("/", "_").replace(".", "").replace(" ", "_")
    name = name.replace("-", "_").replace(":", "_").replace("*", "_").replace("'", "_")
    name = name.replace("+", "_").replace("&", "_").replace("!", "_").replace("×", "_")

    # 去除连续的下划线
    while "__" in name:
        name = name.replace("__", "_")

    # 去除首尾下划线
    if name.startswith("_"):
        name = name[1:]
    if name.endswith("_"):
        name = name[:-1]

    return name


def get_sqlite_type_from_series(series: pd.Series) -> str:
    """
    根据 pandas Series 推断 SQLite 数据类型

    Args:
        series: pandas Series 对象

    Returns:
        SQLite 数据类型字符串
    """
    dtype = str(series.dtype)
    if "int" in dtype:
        return "INT"
    elif "float" in dtype:
        return "REAL"
    elif "bool" in dtype:
        return "BOOLEAN"
    elif "datetime" in dtype:
        return "TEXT"
    else:
        return "TEXT"


def generate_create_table_with_comments(df: pd.DataFrame, table_name: str) -> str:
    """
    根据 DataFrame 生成带注释的 CREATE TABLE 语句

    Args:
        df: pandas DataFrame
        table_name: 表名

    Returns:
        CREATE TABLE SQL 语句
    """
    fields = []
    for col in df.columns:
        col_type = get_sqlite_type_from_series(df[col])
        non_nulls = df[col].dropna()
        example_value = ""

        if not non_nulls.empty:
            example_value = str(random.choice(non_nulls.values))
            example_value = example_value.replace("\n", " ").replace("'", "'").replace('"', '"')

        # 截断过长的样例值
        if len(example_value) > 20:
            example_value = f'{example_value[:10]}...'

        comment = f" COMMENT '样例：{example_value}'" if example_value else ""
        fields.append(f"`{col}` {col_type}{comment}")

    return f"CREATE TABLE {table_name} ({', '.join(fields)});"


def inject_excel_to_db(
    excel_path: str,
    sheet_name: str,
    table_name: str,
    db_path: str,
    if_exists: str = "replace"
) -> Dict[str, Any]:
    """
    将 Excel 文件导入 SQLite 数据库

    Args:
        excel_path: Excel 文件路径
        sheet_name: Sheet 名称
        table_name: 目标表名
        db_path: 数据库路径
        if_exists: 表存在时的处理方式 ("fail", "replace", "append")

    Returns:
        包含导入结果的字典

    Raises:
        FileNotFoundError: Excel 文件不存在
        Exception: 导入过程中的其他错误
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_path}")

    # 读取 Excel
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    original_columns = df.columns.tolist()

    # 标准化列名
    df.columns = [normalize_column_name(c) for c in df.columns]
    normalized_columns = df.columns.tolist()

    # 连接数据库并导入
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        row_count = len(df)
        col_count = len(df.columns)
    finally:
        conn.close()

    # 生成建表语句
    create_statement = generate_create_table_with_comments(df, table_name)

    return {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": col_count,
        "original_columns": original_columns,
        "normalized_columns": normalized_columns,
        "create_statement": create_statement
    }


def update_db_config(
    db_path: str,
    output_path: str,
    mode: str = "add"
) -> Dict[str, Any]:
    """
    扫描数据库结构并输出到 JSON 文件

    Args:
        db_path: 数据库路径
        output_path: 输出 JSON 文件路径
        mode: 更新模式 ("add": 仅新增, "replace": 完全替换)

    Returns:
        数据库配置字典

    Raises:
        FileNotFoundError: 数据库文件不存在
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")

    # 读取旧配置（add 模式）
    old_config = {}
    if os.path.exists(output_path) and mode == "add":
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                old_config = json.load(f)
        except Exception as e:
            print(f"⚠️ 读取旧配置失败，将重新生成: {e}")

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [t[0] for t in cursor.fetchall() if not t[0].startswith("sqlite_")]

    # 初始化配置
    db_schema = {} if mode == "replace" else old_config.copy()

    new_tables = []
    updated_tables = []

    for table in tables:
        # add 模式下跳过已存在的表
        if mode == "add" and table in db_schema:
            continue

        try:
            df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 200;", conn)
            db_schema[table] = {"build": generate_create_table_with_comments(df, table)}

            if table in old_config:
                updated_tables.append(table)
            else:
                new_tables.append(table)
        except Exception as e:
            print(f"⚠️ 无法读取表 {table}: {e}")

    conn.close()

    # 写入配置文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db_schema, f, ensure_ascii=False, indent=2)

    return {
        "total_tables": len(db_schema),
        "new_tables": new_tables,
        "updated_tables": updated_tables,
        "mode": mode,
        "config_path": output_path
    }


def get_excel_sheets(excel_path: str) -> list:
    """
    获取 Excel 文件中的所有 Sheet 名称

    Args:
        excel_path: Excel 文件路径

    Returns:
        Sheet 名称列表
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_path}")

    excel_file = pd.ExcelFile(excel_path)
    return excel_file.sheet_names
