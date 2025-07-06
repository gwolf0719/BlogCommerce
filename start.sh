#!/bin/bash

# BlogCommerce 統一啟動腳本 
# 作者: BlogCommerce 開發團隊
# 日期: 2024-07-06
# 版本: 1.0.0
# 功能: 統一的服務啟動腳本，支援開發模式和生產模式

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 腳本標題
echo -e "${BLUE}🚀 BlogCommerce 啟動程序${NC}"
echo "================================"

# 預設設定
DEFAULT_MODE="prod"
DEFAULT_PORT=8002  # 根據記憶中的端口設定
MODE=${1:-$DEFAULT_MODE}
PORT=${2:-$DEFAULT_PORT}

# 顯示啟動模式
echo -e "${YELLOW}📋 啟動參數:${NC}"
echo "   - 模式: $MODE"
echo "   - 端口: $PORT"
echo "================================"

# 虛擬環境設定
VENV_PY=".venv/bin/python"

# 檢查虛擬環境
setup_venv() {
    echo -e "${BLUE}🔧 設定虛擬環境...${NC}"
    if [ ! -f "$VENV_PY" ]; then
        echo -e "${YELLOW}⚠️  虛擬環境不存在，正在建立...${NC}"
        if ! command -v python &> /dev/null; then
            python3 -m venv .venv
        else
            python -m venv .venv
        fi
    fi
    
    source .venv/bin/activate
    echo -e "${GREEN}✅ 虛擬環境已啟動${NC}"
    
    # 安裝依賴
    echo -e "${BLUE}📦 安裝 Python 依賴...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python 依賴安裝完成${NC}"
}

# 檢查端口
check_port() {
    echo -e "${BLUE}🔎 檢查端口 $PORT...${NC}"
    PID=$(lsof -t -i:$PORT)
    
    if [ -n "$PID" ]; then
        echo -e "${YELLOW}⚠️  端口 $PORT 已被進程 ID: $PID 佔用，正在嘗試終止...${NC}"
        kill -9 $PID
        sleep 2
        
        if [ -n "$(lsof -t -i:$PORT)" ]; then
            echo -e "${RED}❌ 終止進程失敗，請手動處理${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ 成功釋放端口 $PORT${NC}"
        fi
    else
        echo -e "${GREEN}✅ 端口 $PORT 可用${NC}"
    fi
}

# 建置前端（生產模式）
build_frontend() {
    echo -e "${BLUE}🏗️  建置前端管理後台...${NC}"
    cd frontend || { echo -e "${RED}❌ 'frontend' 目錄不存在${NC}"; exit 1; }
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ 'npm' 未安裝，請先安裝 Node.js 和 npm${NC}"
        exit 1
    fi
    
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 'npm install' 失敗${NC}"
        exit 1
    fi
    
    npm run build
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 'npm run build' 失敗${NC}"
        exit 1
    fi
    
    cd ..
    echo -e "${GREEN}✅ 前端建置完成${NC}"
}

# 啟動開發模式前端
start_dev_frontend() {
    echo -e "${BLUE}🚀 啟動開發模式前端服務器...${NC}"
    cd frontend || { echo -e "${RED}❌ 'frontend' 目錄不存在${NC}"; exit 1; }
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ 'npm' 未安裝，請先安裝 Node.js 和 npm${NC}"
        exit 1
    fi
    
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 'npm install' 失敗${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 前端開發服務器將在 http://localhost:3000 啟動${NC}"
    npm run dev &
    
    cd ..
}

# 啟動後端服務器
start_backend() {
    echo -e "${BLUE}🚀 啟動 FastAPI 後端服務器...${NC}"
    echo "   - Host: 0.0.0.0"
    echo "   - Port: $PORT"
    echo "   - 模式: $MODE"
    
    # 檢查 uvicorn 是否存在
    if ! "$VENV_PY" -m uvicorn --version &> /dev/null; then
        echo -e "${RED}❌ uvicorn 未安裝${NC}"
        exit 1
    fi
    
    # 根據模式啟動
    if [ "$MODE" == "dev" ]; then
        echo -e "${GREEN}✅ 開發模式啟動中...${NC}"
        "$VENV_PY" -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
    else
        echo -e "${GREEN}✅ 生產模式啟動中...${NC}"
        "$VENV_PY" -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
    fi
}

# 主要執行邏輯
main() {
    # 設定虛擬環境
    setup_venv
    
    # 檢查端口
    check_port
    
    # 根據模式執行相應的操作
    case $MODE in
        "dev")
            echo -e "${YELLOW}🔧 開發模式啟動${NC}"
            start_dev_frontend
            sleep 3  # 等待前端啟動
            start_backend
            ;;
        "prod")
            echo -e "${YELLOW}🏭 生產模式啟動${NC}"
            build_frontend
            start_backend
            ;;
        *)
            echo -e "${RED}❌ 未知的模式: $MODE${NC}"
            echo "使用方式: $0 [dev|prod] [port]"
            echo "範例:"
            echo "  $0 dev      # 開發模式，預設端口 $DEFAULT_PORT"
            echo "  $0 prod     # 生產模式，預設端口 $DEFAULT_PORT"
            echo "  $0 dev 8001 # 開發模式，指定端口 8001"
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@" 