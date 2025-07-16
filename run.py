#!/usr/bin/env python3
"""
BlogCommerce 啟動腳本
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    ) 