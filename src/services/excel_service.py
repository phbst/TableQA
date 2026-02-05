# -*- coding: utf-8 -*-
"""
Excel 导入服务模块
"""
from typing import Dict, Any, List
from ..utils.excel_importer import (
    inject_excel_to_db,
    update_db_config,
    get_excel_sheets
)
from ..config.settings import DB_PATH, DB_CONFIG_FILE
from ..config.config_loader import reload_db_config


class ExcelImportService:
    """Excel 导入服务类"""

    @staticmethod
    def import_excel(
        excel_path: str,
        sheet_name: str,
        table_name: str,
        if_exists: str = "replace"
    ) -> Dict[str, Any]:
        """
        导入 Excel 文件到数据库

        Args:
            excel_path: Excel 文件路径
            sheet_name: Sheet 名称
            table_name: 目标表名
            if_exists: 表存在时的处理方式

        Returns:
            导入结果字典
        """
        return inject_excel_to_db(
            excel_path=excel_path,
            sheet_name=sheet_name,
            table_name=table_name,
            db_path=DB_PATH,
            if_exists=if_exists
        )

    @staticmethod
    def get_sheets(excel_path: str) -> List[str]:
        """
        获取 Excel 文件中的所有 Sheet

        Args:
            excel_path: Excel 文件路径

        Returns:
            Sheet 名称列表
        """
        return get_excel_sheets(excel_path)

    @staticmethod
    def update_config(mode: str = "add") -> Dict[str, Any]:
        """
        更新数据库配置文件

        Args:
            mode: 更新模式 ("add" 或 "replace")

        Returns:
            更新结果字典
        """
        result = update_db_config(
            db_path=DB_PATH,
            output_path=DB_CONFIG_FILE,
            mode=mode
        )

        # 自动重载内存中的配置
        if reload_db_config():
            print("[INFO] 配置已自动重载到内存")
        else:
            print("[WARNING] 配置重载失败")

        return result

    @staticmethod
    def batch_import(
        configs: List[Dict[str, str]],
        if_exists: str = "replace",
        auto_update_config: bool = True
    ) -> Dict[str, Any]:
        """
        批量导入 Excel 文件

        Args:
            configs: 导入配置列表
            if_exists: 表存在时的处理方式
            auto_update_config: 是否自动更新配置文件

        Returns:
            批量导入结果
        """
        results = []
        succeeded = 0
        failed = 0

        for cfg in configs:
            try:
                result = inject_excel_to_db(
                    excel_path=cfg["excel_path"],
                    sheet_name=cfg["sheet_name"],
                    table_name=cfg["table_name"],
                    db_path=DB_PATH,
                    if_exists=if_exists
                )
                results.append({
                    "table_name": cfg["table_name"],
                    "success": True,
                    "row_count": result["row_count"],
                    "error": None
                })
                succeeded += 1
            except Exception as e:
                results.append({
                    "table_name": cfg["table_name"],
                    "success": False,
                    "row_count": None,
                    "error": str(e)
                })
                failed += 1

        # 自动更新配置
        config_updated = False
        if auto_update_config and succeeded > 0:
            try:
                update_db_config(DB_PATH, DB_CONFIG_FILE, mode="add")
                config_updated = True
                # 自动重载内存中的配置
                if reload_db_config():
                    print("[INFO] 批量导入后配置已自动重载到内存")
                else:
                    print("[WARNING] 批量导入后配置重载失败")
            except Exception as e:
                print(f"[WARNING] 配置文件更新失败: {e}")

        return {
            "total": len(configs),
            "succeeded": succeeded,
            "failed": failed,
            "results": results,
            "config_updated": config_updated
        }
