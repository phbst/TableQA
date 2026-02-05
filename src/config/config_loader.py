# -*- coding: utf-8 -*-
"""
配置加载器
"""
import json
from typing import Optional, Dict, Any
from .settings import DB_CONFIG_FILE, MODEL_CONFIG_FILE

# 全局变量
db_config: Optional[Dict[str, Any]] = None
model_config: Optional[Dict[str, Any]] = None


def load_db_config() -> bool:
    """加载数据库配置"""
    global db_config
    try:
        with open(DB_CONFIG_FILE, "r", encoding="utf-8") as f:
            db_config = json.load(f)
        print(f"[INFO] 成功加载数据库配置，包含 {len(db_config)} 个表")
        return True
    except Exception as e:
        print(f"[ERROR] 加载数据库配置失败: {e}")
        return False


def load_model_config() -> bool:
    """加载模型配置"""
    global model_config
    try:
        with open(MODEL_CONFIG_FILE, "r", encoding="utf-8") as f:
            model_config = json.load(f)
        print(f"[INFO] 成功加载模型配置，包含 {len(model_config['models'])} 个模型")
        return True
    except Exception as e:
        print(f"[ERROR] 加载模型配置失败: {e}")
        return False


def get_db_config() -> Optional[Dict[str, Any]]:
    """获取数据库配置"""
    return db_config


def get_model_config() -> Optional[Dict[str, Any]]:
    """获取模型配置"""
    return model_config


def reload_db_config() -> bool:
    """重新加载数据库配置（用于动态更新）"""
    return load_db_config()


def reload_model_config() -> bool:
    """重新加载模型配置（用于动态更新）"""
    return load_model_config()
