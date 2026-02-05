# -*- coding: utf-8 -*-
"""
应用配置常量
"""

# --- NL2SQL 原始配置 ---
DB_PATH = "./data/sqlite3.db"
PROMPT_TEMPLATE_FILE = "./config/infer.template"
DB_CONFIG_FILE = "./config/config.json"
MODEL_CONFIG_FILE = "./config/model_config.json"

TEMPERATURE = 0
REQUEST_TIMEOUT = 30  # 统一请求超时时间
LOG_FILE = "query_logs.jsonl"  # 日志文件路径
