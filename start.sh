#!/bin/bash
# BlogCommerce 統一啟動腳本
# 版本: 2.0.0
# 功能: 支援開發與生產模式，並自動化前端建置與後端服務。

# --- 配置 ---
# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設端口
BACKEND_PORT=8002
FRONTEND_PORT=3000

# --- 函數定義 ---

# 顯示標題
print_header() {
    echo -e "${BLUE}🚀 BlogCommerce 啟動程序 v2.0.0 ${NC}"
    echo "========================================"
}

# 檢查並清理端口
kill_process_on_port() {
    local port=$1
    local service_name=$2
    echo -e "${YELLOW}Checking port ${port} for ${service_name}...${NC}"
    local pid=$(lsof -t -i:${port})

    if [ -n "$pid" ]; then
        echo -e "${RED}Port ${port} is in use by PID ${pid}. Terminating...${NC}"
        kill -9 ${pid}
        sleep 1
        echo -e "${GREEN}Port ${port} has been freed.${NC}"
    else
        echo -e "${GREEN}Port ${port} is free.${NC}"
    fi
}

# --- 主邏輯 ---

print_header

# 決定模式 (dev or prod)
MODE=${1:-"prod"} # 如果沒有參數，預設為 'prod'

# 啟動虛擬環境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated.${NC}"
else
    echo -e "${RED}❌ Virtual environment '.venv' not found. Please run 'uv venv .venv' first.${NC}"
    exit 1
fi

if [ "$MODE" = "dev" ]; then
    # --- 開發模式 ---
    echo -e "${YELLOW}🔧 Starting in DEVELOPMENT mode...${NC}"

    # 清理相關端口
    kill_process_on_port $BACKEND_PORT "FastAPI Backend"
    kill_process_on_port $FRONTEND_PORT "Vite Frontend"

    # 啟動前端開發伺服器 (背景執行)
    echo -e "${BLUE}Starting Vite dev server in the background...${NC}"
    (cd admin-src && npm install && npm run dev) &
    FRONTEND_PID=$!
    echo -e "${GREEN}✅ Frontend dev server started with PID ${FRONTEND_PID}.${NC}"
    echo -e "   Admin panel will be available at: http://localhost:${FRONTEND_PORT}/admin"

    # 啟動後端伺服器
    echo -e "${BLUE}Starting FastAPI backend server...${NC}"
    export APP_ENV=development
    uv run run.py
    
    # 當後端停止時，也停止前端
    kill $FRONTEND_PID

elif [ "$MODE" = "prod" ]; then
    # --- 生產模式 ---
    echo -e "${YELLOW}🏭 Starting in PRODUCTION mode...${NC}"

    # 清理後端端口
    kill_process_on_port $BACKEND_PORT "FastAPI Backend"

    # 建置前端
    echo -e "${BLUE}Building frontend for production...${NC}"
    (cd admin-src && npm install && npm run build)
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Frontend build failed. Aborting.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Frontend build successful.${NC}"

    # 啟動後端伺服器
    echo -e "${BLUE}Starting FastAPI backend server...${NC}"
    export APP_ENV=production
    uv run run.py
    echo -e "   Application will be available at: http://localhost:${BACKEND_PORT}"
    echo -e "   Admin panel will be available at: http://localhost:${BACKEND_PORT}/admin"

else
    echo -e "${RED}❌ Invalid mode specified: '$MODE'. Use 'dev' or 'prod'.${NC}"
    exit 1
fi

echo -e "${BLUE}BlogCommerce has shut down.${NC}"