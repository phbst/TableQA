# -*- coding: utf-8 -*-
from .query_routes import router as query_router
from .health_routes import router as health_router
from .excel_routes import router as excel_router
from .chat_routes import router as chat_router

__all__ = [
    "query_router",
    "health_router",
    "excel_router",
    "chat_router",
]
