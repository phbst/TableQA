# -*- coding: utf-8 -*-
"""
数据库服务
"""
from typing import List, Dict, Any, Optional
from ..config import get_db_config


class DatabaseService:
    """数据库相关服务"""

    @staticmethod
    def get_all_tables() -> List[str]:
        """获取所有表名"""
        db_config = get_db_config()
        if not db_config:
            return []
        return list(db_config.keys())

    @staticmethod
    def get_table_schema(table_name: str) -> Optional[Dict[str, Any]]:
        """获取表结构"""
        db_config = get_db_config()
        if not db_config or table_name not in db_config:
            return None
        return {
            "table_name": table_name,
            "build_statement": db_config[table_name]["build"]
        }

    @staticmethod
    def table_exists(table_name: str) -> bool:
        """检查表是否存在"""
        db_config = get_db_config()
        if not db_config:
            return False
        return table_name in db_config
