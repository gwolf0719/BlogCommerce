#!/bin/bash

# BlogCommerce 停止服務腳本
# 停止所有相關的前後端服務

echo "🛑 BlogCommerce 停止服務腳本"
echo "=================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 停止 FastAPI 服務 (通常運行在 8000 端口)
echo -e "${YELLOW}🔍 查找並停止 FastAPI 服務...${NC}"
FASTAPI_PID=$(lsof -ti:8000)
if [ ! -z "$FASTAPI_PID" ]; then
    kill -9 $FASTAPI_PID
    echo -e "${GREEN}✅ FastAPI 服務已停止${NC}"
else
    echo -e "${YELLOW}⚠️  未找到運行中的 FastAPI 服務${NC}"
fi

# 停止 Vite 開發服務器 (通常運行在 5173 端口)
echo -e "${YELLOW}🔍 查找並停止 Vite 開發服務器...${NC}"
VITE_PID=$(lsof -ti:5173)
if [ ! -z "$VITE_PID" ]; then
    kill -9 $VITE_PID
    echo -e "${GREEN}✅ Vite 開發服務器已停止${NC}"
else
    echo -e "${YELLOW}⚠️  未找到運行中的 Vite 開發服務器${NC}"
fi

# 停止所有可能的 uvicorn 進程
echo -e "${YELLOW}🔍 查找並停止所有 uvicorn 進程...${NC}"
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app")
if [ ! -z "$UVICORN_PIDS" ]; then
    echo $UVICORN_PIDS | xargs kill -9
    echo -e "${GREEN}✅ 所有 uvicorn 進程已停止${NC}"
else
    echo -e "${YELLOW}⚠️  未找到運行中的 uvicorn 進程${NC}"
fi

# 停止所有可能的 node 開發服務器
echo -e "${YELLOW}🔍 查找並停止 Vue 開發服務器進程...${NC}"
NODE_PIDS=$(pgrep -f "vite.*dev")
if [ ! -z "$NODE_PIDS" ]; then
    echo $NODE_PIDS | xargs kill -9
    echo -e "${GREEN}✅ Vue 開發服務器進程已停止${NC}"
else
    echo -e "${YELLOW}⚠️  未找到運行中的 Vue 開發服務器進程${NC}"
fi

echo -e "${GREEN}=================================="
echo -e "🎉 所有服務已停止完成！"
echo -e "==================================" 