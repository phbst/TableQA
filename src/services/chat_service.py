# -*- coding: utf-8 -*-
"""
Chat 对话服务
"""
import time
import requests
from typing import Optional
from fastapi import HTTPException

from ..config import TEMPERATURE, REQUEST_TIMEOUT, get_model_config


CHAT_TEMPLATE_FILE = "./config/chat.template"


def call_chat_api(table_info: str, question: str, model_name: Optional[str] = None) -> str:
    """
    调用大模型接口进行对话

    Args:
        table_info: 表结构信息字符串
        question: 用户问题
        model_name: 模型名称，不指定则使用默认模型

    Returns:
        模型的回答

    Raises:
        HTTPException: 当模型不存在、已禁用或调用失败时
    """
    model_config = get_model_config()

    if not model_name:
        model_name = model_config.get("default_model", "SFT-Qwen3-8B")

    if model_name not in model_config["models"]:
        raise HTTPException(status_code=400, detail=f"模型 '{model_name}' 不存在")

    model_info = model_config["models"][model_name]

    if not model_info.get("enabled", True):
        raise HTTPException(status_code=400, detail=f"模型 '{model_name}' 已禁用")

    # 读取 prompt 模板
    try:
        with open(CHAT_TEMPLATE_FILE, encoding="utf-8") as f:
            prompt = f.read().format(table_info=table_info, question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取 chat 模板失败: {e}")

    # 构造请求
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

    # 调用模型 API
    try:
        start = time.time()
        resp = requests.post(api_url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        latency = time.time() - start
        print(f"[INFO] Chat 模型 {model_name} 响应耗时: {latency:.2f}s")
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用模型 {model_name} 失败: {e}")
