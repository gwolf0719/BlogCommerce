#!/bin/bash

# --- BlogCommerce 統一啟動腳本 ---

# 預設 Port
DEFAULT_PORT=8001
PORT=${1:-$DEFAULT_PORT}

# 腳本標題
echo "🚀 BlogCommerce 啟動程序"
echo "--------------------------------"

# 0. 強制使用 .venv 虛擬環境
VENV_PY=".venv/bin/python"
if [ ! -f "$VENV_PY" ]; then
    # 建立虛擬環境 如果 python 這個指令不能用就用 python3 來建立
    if ! command -v python &> /dev/null; then
        python3 -m venv .venv
    else
        python -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

pip install -r requirements.txt

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
echo "✅ 前端建置完成，產物已輸出至 app/static。"

# 3. (省略 Admin SPA 複製步驟，因產物已在正確位置)

# 4. 啟動後端伺服器
echo "🚀 正在啟動 FastAPI 後端伺服器..."
echo "   - Host: 0.0.0.0"
echo "   - Port: $PORT"

# 檢查 .venv/bin/python 和 uvicorn 是否存在
if ! "$VENV_PY" -m uvicorn --version &> /dev/null
then
    echo "❌ .venv/bin/python 或 uvicorn 未安裝，請確保虛擬環境已設定且 'requirements.txt' 已安裝。"
    exit 1
fi

# 使用 .venv/bin/python 啟動
"$VENV_PY" -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
