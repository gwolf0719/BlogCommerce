#!/bin/bash

# --- BlogCommerce 統一啟動腳本 ---

# 預設 Port
DEFAULT_PORT=8001
PORT=${1:-$DEFAULT_PORT}

# 後端靜態檔案目錄 (給 Admin SPA)
ADMIN_DIST_DIR="frontend/dist"
BACKEND_ADMIN_DIR="app/static/admin"

# 腳本標題
echo "🚀 BlogCommerce 啟動程序"
echo "--------------------------------"

# 1. 檢查 Port 是否被佔用，並終止佔用進程
echo "🔎 正在檢查 Port: $PORT..."
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "⚠️ Port $PORT 已被進程 ID: $PID 佔用。正在嘗試終止..."
    kill -9 $PID
    sleep 2
    # 再次檢查
    if [ -n "$(lsof -t -i:$PORT)" ]; then
        echo "❌ 終止進程失敗，請手動處理。"
        exit 1
    else
        echo "✅ 成功釋放 Port $PORT。"
    fi
else
    echo "✅ Port $PORT 可用。"
fi

# 2. 建立前端管理後台
echo "🏗️ 正在建置前端管理後台 (Admin SPA)..."
cd frontend || { echo "❌ 'frontend' 目錄不存在。"; exit 1; }

# 檢查 npm 是否安裝
if ! command -v npm &> /dev/null
then
    echo "❌ 'npm' 未安裝，請先安裝 Node.js 和 npm。"
    exit 1
fi

npm install
if [ $? -ne 0 ]; then
    echo "❌ 'npm install' 失敗，請檢查 Node.js 環境和 'package.json'。"
    exit 1
fi

npm run build
if [ $? -ne 0 ]; then
    echo "❌ 'npm run build' 失敗，請檢查 Vite 設定。"
    exit 1
fi

cd ..
echo "✅ 前端建置完成。"

# 3. 將建置好的前端檔案移動到後端靜態目錄
echo "📦 正在將 Admin SPA 部署到後端靜態目錄..."
# 建立目標目錄
mkdir -p $BACKEND_ADMIN_DIR

# 清空舊檔案
rm -rf $BACKEND_ADMIN_DIR/*

# 複製新檔案
cp -r $ADMIN_DIST_DIR/* $BACKEND_ADMIN_DIR/
if [ $? -ne 0 ]; then
    echo "❌ 複製 Admin SPA 檔案失敗。"
    exit 1
fi
echo "✅ Admin SPA 已成功部署。"


# 4. 啟動後端伺服器
echo "🚀 正在啟動 FastAPI 後端伺服器..."
echo "   - Host: 0.0.0.0"
echo "   - Port: $PORT"

# 檢查 Python 和 uvicorn 是否存在
if ! command -v python &> /dev/null || ! python -m uvicorn --version &> /dev/null
then
    echo "❌ Python 或 uvicorn 未安裝，請確保 Python 環境已設定且 'requirements.txt' 已安裝。"
    exit 1
fi

# 使用 uvicorn 啟動
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
