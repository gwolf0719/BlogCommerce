#!/bin/bash

# BlogCommerce 啟動腳本
# 使用方式:
# ./start.sh        - 生產模式（默認，前端構建後啟動）
# ./start.sh dev    - 開發模式（前端自動重新構建）
# ./start.sh hot    - 熱重載模式（前後端分離）
# ./start.sh build  - 只構建前端

MODE=${1:-"prod"}

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查是否安裝了必要的依賴
check_requirements() {
    echo -e "${BLUE}🔍 檢查系統需求...${NC}"
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安裝，請先安裝 Node.js${NC}"
        exit 1
    fi
    
    # 檢查 npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安裝，請先安裝 npm${NC}"
        exit 1
    fi
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安裝，請先安裝 Python3${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 系統需求檢查完成${NC}"
}

# 檢查並安裝前端依賴
setup_frontend() {
    echo -e "${BLUE}🔧 設定前端環境...${NC}"
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 安裝前端依賴...${NC}"
        npm install
    fi
    
    cd ..
    echo -e "${GREEN}✅ 前端環境設定完成${NC}"
}

# 檢查並設定後端環境
setup_backend() {
    echo -e "${BLUE}🔧 設定後端環境...${NC}"
    
    # 檢查是否有虛擬環境
    if [ -d "venv" ]; then
        echo -e "${YELLOW}🐍 使用現有虛擬環境...${NC}"
        source venv/bin/activate
    elif [ -d "env" ]; then
        echo -e "${YELLOW}🐍 使用現有虛擬環境...${NC}"
        source env/bin/activate
    else
        echo -e "${YELLOW}🐍 創建新的虛擬環境...${NC}"
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # 安裝 Python 依賴
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}📦 安裝後端依賴...${NC}"
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ 後端環境設定完成${NC}"
}

# 構建前端
build_frontend() {
    echo -e "${BLUE}🏗️  構建前端...${NC}"
    cd frontend
    npm run build
    cd ..
    
    # 複製構建好的 HTML 到正確位置
    if [ -f "app/static/public/index.html" ]; then
        cp app/static/public/index.html app/static/index.html
        echo -e "${GREEN}✅ 已更新 index.html${NC}"
    fi
    
    echo -e "${GREEN}✅ 前端構建完成${NC}"
}

# 啟動後端服務
start_backend() {
    echo -e "${BLUE}🚀 啟動後端服務...${NC}"
    
    # 檢查並啟用虛擬環境
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "env" ]; then
        source env/bin/activate
    fi
    
    # 啟動 FastAPI 服務（從項目根目錄運行）
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    echo -e "${GREEN}✅ 後端服務已啟動 (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}📡 後端服務地址: http://localhost:8000${NC}"
}

# 啟動前端開發服務
start_frontend_dev() {
    echo -e "${BLUE}🚀 啟動前端開發服務...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ 前端開發服務已啟動 (PID: $FRONTEND_PID)${NC}"
    echo -e "${BLUE}📡 前端服務地址: http://localhost:5173${NC}"
}

# 啟動前端自動構建監聽
start_frontend_watch() {
    echo -e "${BLUE}🚀 啟動前端自動構建監聽...${NC}"
    cd frontend
    
    # 先進行一次初始構建
    npm run build
    
    # 複製構建好的 HTML 到正確位置
    if [ -f "../app/static/public/index.html" ]; then
        cp ../app/static/public/index.html ../app/static/index.html
        echo -e "${GREEN}✅ 已更新 index.html${NC}"
    fi
    
    # 創建一個腳本來監聽構建完成並自動複製 index.html
    cat > watch_build.sh << 'EOF'
#!/bin/bash
npx vite build --watch &
VITE_PID=$!

# 檢查是否有 fswatch
if command -v fswatch &> /dev/null; then
    # 使用 fswatch 監聽目錄變化
    fswatch -o ../app/static/public/ | while read f; do
        if [ -f "../app/static/public/index.html" ]; then
            cp ../app/static/public/index.html ../app/static/index.html
            echo "$(date '+%H:%M:%S') ✅ 已自動更新 index.html (fswatch)"
        fi
    done &
    WATCH_PID=$!
else
    # 沒有 fswatch，使用定期檢查方式
    while true; do
        sleep 3
        if [ -f "../app/static/public/index.html" ]; then
            # 檢查文件是否有變化（比較修改時間）
            if [ "../app/static/public/index.html" -nt "../app/static/index.html" ]; then
                cp ../app/static/public/index.html ../app/static/index.html
                echo "$(date '+%H:%M:%S') ✅ 已自動更新 index.html (polling)"
            fi
        fi
    done &
    WATCH_PID=$!
fi

# 捕捉信號並清理
trap 'kill $VITE_PID $WATCH_PID 2>/dev/null; exit' SIGTERM SIGINT

wait $VITE_PID
EOF
    
    chmod +x watch_build.sh
    
    # 檢查是否有 fswatch，顯示相應信息
    if command -v fswatch &> /dev/null; then
        echo -e "${GREEN}✅ 使用 fswatch 進行文件監聽${NC}"
    else
        echo -e "${YELLOW}⚠️  fswatch 未安裝，使用定期檢查模式${NC}"
        echo -e "${YELLOW}💡 安裝 fswatch 可獲得更好的文件監聽體驗: brew install fswatch${NC}"
    fi
    
    ./watch_build.sh &
    
    FRONTEND_WATCH_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ 前端自動構建監聽已啟動 (PID: $FRONTEND_WATCH_PID)${NC}"
    echo -e "${YELLOW}💡 文件變化時會自動重新構建到 app/static${NC}"
}

# 清理進程
cleanup() {
    echo -e "\n${YELLOW}🛑 正在關閉服務...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 後端服務已關閉${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 前端開發服務已關閉${NC}"
    fi
    
    if [ ! -z "$FRONTEND_WATCH_PID" ]; then
        kill $FRONTEND_WATCH_PID 2>/dev/null
        echo -e "${GREEN}✅ 前端自動構建已關閉${NC}"
    fi
    
    # 殺死所有相關進程
    pkill -f "uvicorn.*main:app" 2>/dev/null
    pkill -f "vite.*dev" 2>/dev/null
    pkill -f "vite.*build.*watch" 2>/dev/null
    pkill -f "fswatch" 2>/dev/null
    
    # 清理臨時腳本
    rm -f frontend/watch_build.sh 2>/dev/null
    
    echo -e "${GREEN}🎉 所有服務已關閉${NC}"
    exit 0
}

# 捕捉 Ctrl+C 信號
trap cleanup SIGINT

# 顯示使用說明
show_usage() {
    echo -e "${BLUE}📖 BlogCommerce 啟動腳本使用說明${NC}"
    echo -e "${YELLOW}使用方式:${NC}"
    echo -e "  ./start.sh         - 生產模式（默認）"
    echo -e "  ./start.sh dev     - 開發模式（自動重新構建）"
    echo -e "  ./start.sh hot     - 熱重載模式（前後端分離）"
    echo -e "  ./start.sh prod    - 生產模式"
    echo -e "  ./start.sh build   - 只構建前端"
    echo -e "  ./start.sh help    - 顯示此說明"
    echo ""
    echo -e "${YELLOW}生產模式 (prod - 默認):${NC}"
    echo -e "  - 前端會先構建成靜態文件"
    echo -e "  - 統一服務: http://localhost:8000"
    echo -e "  - 管理後台: http://localhost:8000/admin"
    echo ""
    echo -e "${YELLOW}開發模式 (dev):${NC}"
    echo -e "  - 統一入口: http://localhost:8000"
    echo -e "  - 管理後台: http://localhost:8000/admin"
    echo -e "  - 前端文件變化時自動重新構建"
    echo -e "  - 適合前端開發，修改即生效"
    echo ""
    echo -e "${YELLOW}熱重載模式 (hot):${NC}"
    echo -e "  - 前端開發服務: http://localhost:5173"
    echo -e "  - 後端API服務: http://localhost:8000"
    echo -e "  - 支援熱重載，修改代碼後立即更新"
    echo -e "  - 適合前端組件開發除錯"
}

# 主邏輯
case $MODE in
    "dev")
        echo -e "${GREEN}🎯 啟動開發模式（自動重新構建）${NC}"
        check_requirements
        setup_backend
        setup_frontend
        start_backend
        sleep 2
        start_frontend_watch
        
        echo -e "\n${GREEN}🎉 開發服務已啟動！${NC}"
        echo -e "${BLUE}📡 管理後台: http://localhost:8000/admin${NC}"
        echo -e "${BLUE}📡 後端 API: http://localhost:8000/api${NC}"
        echo -e "${BLUE}📡 前端網站: http://localhost:8000${NC}"
        echo -e "${YELLOW}💡 按 Ctrl+C 停止服務${NC}"
        echo -e "${YELLOW}💡 前端代碼變化時會自動重新構建${NC}"
        
        # 等待信號
        wait
        ;;
        
    "hot")
        echo -e "${GREEN}🎯 啟動熱重載模式${NC}"
        check_requirements
        setup_backend
        setup_frontend
        start_backend
        sleep 3
        start_frontend_dev
        
        echo -e "\n${GREEN}🎉 熱重載服務已啟動！${NC}"
        echo -e "${BLUE}📡 前端開發服務: http://localhost:5173${NC}"
        echo -e "${BLUE}📡 後端 API 服務: http://localhost:8000${NC}"
        echo -e "${YELLOW}💡 按 Ctrl+C 停止所有服務${NC}"
        echo -e "${YELLOW}💡 前端支援熱重載，修改代碼後自動更新${NC}"
        
        # 等待信號
        wait
        ;;
        
    "prod")
        echo -e "${GREEN}🎯 啟動生產模式${NC}"
        check_requirements
        setup_backend
        setup_frontend
        build_frontend
        start_backend
        
        echo -e "\n${GREEN}🎉 生產服務已啟動！${NC}"
        echo -e "${BLUE}📡 服務地址: http://localhost:8000${NC}"
        echo -e "${YELLOW}💡 按 Ctrl+C 停止服務${NC}"
        
        # 等待信號
        wait
        ;;
        
    "build")
        echo -e "${GREEN}🎯 只構建前端${NC}"
        check_requirements
        setup_frontend
        build_frontend
        echo -e "${GREEN}🎉 前端構建完成！${NC}"
        ;;
        
    "help")
        show_usage
        ;;
        
    *)
        echo -e "${RED}❌ 未知的模式: $MODE${NC}"
        show_usage
        exit 1
        ;;
esac 