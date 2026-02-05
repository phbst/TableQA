# -*- coding: utf-8 -*-
"""
SQL 解析工具
"""
import re
from typing import List


def extract_sql(resp: str) -> str:
    """从模型返回文本中提取SQL"""
    if not resp:
        return resp
    text = str(resp).strip()
    pattern = r"```(?:sql)?\s*([\s\S]*?)```"
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def fix_table_name(sql: str, table_names: List[str] = None) -> str:
    """修正表名"""
    return sql
