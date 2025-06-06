#!/bin/bash

# BlogCommerce 快速啟動腳本
# 自動啟動前端和後端服務

set -e  # 如果任何命令失败则退出

echo "🚀 BlogCommerce 快速啟動腳本"
echo "=================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查並創建 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 檔案不存在，正在從 env.example 複製...${NC}"
    cp env.example .env
    echo -e "${GREEN}✅ .env 檔案已創建，請根據需要修改設定${NC}"
fi

# 函數：檢查端口是否被佔用
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${RED}❌ 端口 $port 已被佔用${NC}"
        echo "請先關閉佔用端口 $port 的程序，或修改配置使用其他端口"
        exit 1
    fi
}

# 檢查必要端口
echo "🔍 檢查端口佔用狀況..."
check_port 8000  # FastAPI 預設端口
check_port 5173  # Vite 預設端口

# 啟動後端服務
echo -e "${BLUE}🔧 啟動後端服務 (FastAPI)...${NC}"
cd backend

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虛擬環境不存在，正在創建...${NC}"
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "📦 啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "📥 檢查並安裝 Python 依賴..."
pip install -q -r ../requirements.txt

# 初始化資料庫（如果需要）
if [ ! -f "blog_commerce.db" ]; then
    echo -e "${YELLOW}🗄️  資料庫不存在，正在初始化...${NC}"
    python init_db.py
    echo -e "${GREEN}✅ 資料庫初始化完成${NC}"
fi

# 在背景啟動後端
echo "🚀 啟動 FastAPI 服務器..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# 啟動前端服務
echo -e "${BLUE}🎨 啟動前端服務 (Vue 3)...${NC}"
cd frontend

# 檢查並安裝 Node.js 依賴
if [ ! -d "node_modules" ]; then
    echo "📥 安裝 Node.js 依賴..."
    npm install
fi

# 檢查並創建前端 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  前端 .env 檔案不存在，正在從 env.example 複製...${NC}"
    cp env.example .env
fi

# 在背景啟動前端
echo "🚀 啟動 Vite 開發服務器..."
npm run dev &
FRONTEND_PID=$!

cd ..

# 等待服務啟動
echo -e "${YELLOW}⏳ 等待服務啟動...${NC}"
sleep 5

echo -e "${GREEN}=================================="
echo -e "🎉 服務啟動完成！"
echo -e "=================================="
echo -e "📖 後端 API: ${BLUE}http://localhost:8000${NC}"
echo -e "📖 API 文檔: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "🎨 前端應用: ${BLUE}http://localhost:5173${NC}"
echo -e "=================================="
echo -e "按 ${RED}Ctrl+C${NC} 停止所有服務"
echo -e "${NC}"

# 函數：清理程序
cleanup() {
    echo -e "\n${YELLOW}🛑 正在停止服務...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ 所有服務已停止${NC}"
    exit 0
}

# 捕捉中斷信號
trap cleanup SIGINT SIGTERM

# 保持腳本運行
wait 