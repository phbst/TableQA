#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务启动脚本
"""
import uvicorn
from src.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
