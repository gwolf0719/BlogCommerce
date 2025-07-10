#!/bin/bash

# BlogCommerce 統一啟動腳本 
# 作者: BlogCommerce 開發團隊
# 日期: 2024-07-06
# 版本: 1.1.0
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
DEFAULT_PORT=8002  # 生產模式預設端口
DEV_BACKEND_PORT=8002  # 開發模式後端固定端口
DEV_FRONTEND_PORT=3000  # 開發模式前端固定端口

MODE=${1:-$DEFAULT_MODE}

# 根據模式設定端口
if [ "$MODE" == "dev" ]; then
    PORT=$DEV_BACKEND_PORT  # dev 模式強制使用固定端口
    FRONTEND_PORT=$DEV_FRONTEND_PORT
else
    PORT=${2:-$DEFAULT_PORT}  # 生產模式可以自定義端口
fi

# 顯示啟動模式
echo -e "${YELLOW}📋 啟動參數:${NC}"
echo "   - 模式: $MODE"
echo "   - 後端端口: $PORT"
if [ "$MODE" == "dev" ]; then
    echo "   - 前端端口: $FRONTEND_PORT (固定)"
fi
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

# 資料庫遷移檢查和執行
run_migrations() {
    echo -e "${BLUE}🗃️  檢查資料庫遷移狀態...${NC}"
    
    # 檢查是否有 alembic 目錄和配置
    if [ ! -f "alembic.ini" ]; then
        echo -e "${YELLOW}⚠️  Alembic 配置文件不存在，跳過遷移...${NC}"
        return 0
    fi
    
    if [ ! -d "alembic/versions" ]; then
        echo -e "${YELLOW}⚠️  Alembic versions 目錄不存在，正在建立...${NC}"
        mkdir -p alembic/versions
    fi
    
    # 檢查是否有現有的遷移文件
    local migration_files=$(find alembic/versions -name "*.py" -type f | wc -l)
    
    if [ "$migration_files" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  沒有找到遷移文件，正在建立初始遷移...${NC}"
        
        # 建立初始遷移
        if "$VENV_PY" -m alembic revision --autogenerate -m "Initial migration"; then
            echo -e "${GREEN}✅ 初始遷移建立成功${NC}"
        else
            echo -e "${RED}❌ 初始遷移建立失敗${NC}"
            return 1
        fi
    fi
    
    # 檢查資料庫是否需要遷移
    echo -e "${BLUE}🔄 檢查資料庫遷移狀態...${NC}"
    
    # 嘗試獲取當前資料庫版本
    if "$VENV_PY" -m alembic current &> /dev/null; then
        local current_rev=$("$VENV_PY" -m alembic current 2>/dev/null | head -1)
        local head_rev=$("$VENV_PY" -m alembic heads 2>/dev/null | head -1)
        
        if [ "$current_rev" != "$head_rev" ]; then
            echo -e "${YELLOW}⚠️  資料庫需要遷移，正在執行遷移...${NC}"
            
            # 執行遷移
            if "$VENV_PY" -m alembic upgrade head; then
                echo -e "${GREEN}✅ 資料庫遷移完成${NC}"
            else
                echo -e "${RED}❌ 資料庫遷移失敗${NC}"
                return 1
            fi
        else
            echo -e "${GREEN}✅ 資料庫已是最新版本${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  無法獲取資料庫版本，強制執行遷移...${NC}"
        
        # 強制執行遷移
        if "$VENV_PY" -m alembic upgrade head; then
            echo -e "${GREEN}✅ 資料庫遷移完成${NC}"
        else
            echo -e "${RED}❌ 資料庫遷移失敗${NC}"
            return 1
        fi
    fi
    
    return 0
}

# 強制清理端口（增強版）
force_kill_port() {
    local target_port=$1
    local port_name=$2
    
    echo -e "${BLUE}🔎 檢查端口 $target_port ($port_name)...${NC}"
    
    # 獲取所有佔用該端口的進程ID
    local pids=$(lsof -t -i:$target_port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}⚠️  端口 $target_port 已被進程佔用：$pids${NC}"
        
        # 顯示佔用進程的詳細信息
        echo -e "${YELLOW}   佔用該端口的進程信息：${NC}"
        lsof -i:$target_port 2>/dev/null | head -10
        
        echo -e "${YELLOW}   正在終止這些進程...${NC}"
        
        # 先嘗試優雅地終止進程
        for pid in $pids; do
            if kill -TERM "$pid" 2>/dev/null; then
                echo -e "${BLUE}   發送 TERM 信號給進程 $pid${NC}"
            fi
        done
        
        # 等待 3 秒讓進程優雅退出
        sleep 3
        
        # 檢查是否還有進程佔用端口
        local remaining_pids=$(lsof -t -i:$target_port 2>/dev/null)
        
        if [ -n "$remaining_pids" ]; then
            echo -e "${YELLOW}   優雅終止失敗，強制終止進程...${NC}"
            
            # 強制終止剩餘進程
            for pid in $remaining_pids; do
                if kill -9 "$pid" 2>/dev/null; then
                    echo -e "${BLUE}   強制終止進程 $pid${NC}"
                fi
            done
            
            # 再等待 2 秒
            sleep 2
        fi
        
        # 最終檢查
        local final_check=$(lsof -t -i:$target_port 2>/dev/null)
        if [ -n "$final_check" ]; then
            echo -e "${RED}❌ 無法釋放端口 $target_port，仍有進程佔用：$final_check${NC}"
            echo -e "${RED}   請手動處理或重啟系統${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ 成功釋放端口 $target_port${NC}"
        fi
    else
        echo -e "${GREEN}✅ 端口 $target_port 可用${NC}"
    fi
}

# 檢查端口（保留舊函數名但使用新的強制清理邏輯）
check_port() {
    force_kill_port $PORT "後端服務"
}

# 檢查前端端口
check_frontend_port() {
    if [ "$MODE" == "dev" ]; then
        force_kill_port $FRONTEND_PORT "前端服務"
    fi
}

# 建置前端（生產模式）
build_frontend() {
    echo -e "${BLUE}🏗️  建置前端管理後台...${NC}"
    cd admin-src || { echo -e "${RED}❌ 'admin-src' 目錄不存在${NC}"; exit 1; }
    
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
    cd admin-src || { echo -e "${RED}❌ 'admin-src' 目錄不存在${NC}"; exit 1; }
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ 'npm' 未安裝，請先安裝 Node.js 和 npm${NC}"
        exit 1
    fi
    
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 'npm install' 失敗${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 前端開發服務器將在 http://localhost:$FRONTEND_PORT 啟動${NC}"
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
    
    # 執行資料庫遷移
    if ! run_migrations; then
        echo -e "${RED}❌ 資料庫遷移失敗，停止啟動程序${NC}"
        exit 1
    fi
    
    # 根據模式執行相應的操作
    case $MODE in
        "dev")
            echo -e "${YELLOW}🔧 開發模式啟動${NC}"
            echo -e "${BLUE}   - 固定後端端口: $DEV_BACKEND_PORT${NC}"
            echo -e "${BLUE}   - 固定前端端口: $DEV_FRONTEND_PORT${NC}"
            
            # 檢查並清理端口
            check_frontend_port
            check_port
            
            # 啟動服務
            start_dev_frontend
            sleep 3  # 等待前端啟動
            start_backend
            ;;
        "prod")
            echo -e "${YELLOW}🏭 生產模式啟動${NC}"
            # 檢查後端端口
            check_port
            
            build_frontend
            start_backend
            ;;
        "stop")
            echo -e "${YELLOW}🛑 停止模式 - 清理端口${NC}"
            force_kill_port $DEV_BACKEND_PORT "後端服務"
            force_kill_port $DEV_FRONTEND_PORT "前端服務"
            echo -e "${GREEN}✅ 端口清理完成${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知的模式: $MODE${NC}"
            echo "使用方式: $0 [dev|prod|stop] [port]"
            echo "範例:"
            echo "  $0 dev        # 開發模式，固定端口 $DEV_BACKEND_PORT (後端) + $DEV_FRONTEND_PORT (前端)"
            echo "  $0 prod       # 生產模式，預設端口 $DEFAULT_PORT"
            echo "  $0 prod 8001  # 生產模式，指定端口 8001"
            echo "  $0 stop       # 停止所有服務，清理端口"
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@" 