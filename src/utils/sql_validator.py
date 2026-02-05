# -*- coding: utf-8 -*-
"""
SQL 安全验证工具
"""
import re
from fastapi import HTTPException


def validate_sql_readonly(sql: str):
    """
    静态规则检测：确保 SQL 语句是安全的只读查询
    """
    if not sql:
        raise HTTPException(status_code=400, detail="SQL语句为空")

    # 1. 清理空白字符
    clean_sql = sql.strip()

    # 2. 必须以 SELECT 开头 (忽略大小写)
    # 使用 re.I (IGNORECASE) 确保捕获 Select, select, SELECT 等
    if not re.match(r'^\s*SELECT\b', clean_sql, re.I):
        raise HTTPException(
            status_code=403,
            detail="安全策略拦截：仅允许执行 SELECT 查询语句。"
        )

    # 3. 禁止多条语句执行 (检查分号)
    # 如果有分号，且分号不是在字符串最后，或者分号后还有内容，则拒绝
    if ";" in clean_sql:
        # 允许末尾有唯一的分号，但不允许分号后跟其他字符
        if not re.match(r'^[^;]+;\s*$', clean_sql):
             raise HTTPException(
                status_code=403,
                detail="安全策略拦截：禁止执行多条 SQL 语句（检测到分号）。"
            )

    # 4. 黑名单关键词检测 (使用 \b 单词边界防止误伤字段名)
    # 包含了修改、删除、结构变更及 SQLite 危险元指令
    blacklist = [
        r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bREPLACE\b", r"\bMERGE\b",
        r"\bCREATE\b", r"\bALTER\b", r"\bDROP\b", r"\bTRUNCATE\b",
        r"\bATTACH\b", r"\bDETACH\b", r"\bVACUUM\b", r"\bPRAGMA\b",
        r"\bBEGIN\b", r"\bCOMMIT\b", r"\bROLLBACK\b", r"\bSAVEPOINT\b", r"\bRELEASE\b",
        r"\bEXEC\b", r"\bEXECUTE\b"
    ]

    for pattern in blacklist:
        if re.search(pattern, clean_sql, re.I):
            clean_name = pattern.replace(r"\b", "")
            raise HTTPException(
                status_code=403,
                detail=f"安全策略拦截：检测到禁止使用的关键词 '{clean_name}'。"
            )

    return True
