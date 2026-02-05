# -*- coding: utf-8 -*-
"""
日志记录工具
"""
import json
import os
from typing import Dict, Any
from ..config import LOG_FILE


def save_query_log(record: Dict[str, Any]):
    """保存请求记录到 JSONL 文件"""
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
