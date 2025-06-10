#!/usr/bin/env python3
"""
BlogCommerce 啟動腳本
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    ) 