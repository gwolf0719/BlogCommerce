#!/bin/bash
# BlogCommerce 初始安裝腳本
set -e

echo "\n🛠️  BlogCommerce 安裝向導"
echo "============================\n"

# 1. 檢查 Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 未找到 python3，請先安裝 Python 3.9+"
    exit 1
fi

# 2. 建立虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 建立 Python 虛擬環境..."
    python3 -m venv venv
fi

# 3. 啟用虛擬環境
source venv/bin/activate

# 4. 安裝依賴
echo "📚 安裝後端依賴..."
pip install -r requirements.txt

# 5. 建立環境變數檔
if [ ! -f ".env" ]; then
    echo "📄 建立 .env 設定檔..."
    cp .env.example .env
    echo "請依需求修改 .env 後重新執行此腳本或啟動服務。"
fi

# 6. 初始化資料庫與系統設定
echo "🗄️  初始化資料庫與預設設定..."
python init_db.py
python init_settings.py

# 7. 建立範例資料 (可選)
read -p "是否匯入範例資料？ [y/N] " create_sample
if [[ $create_sample =~ ^[Yy]$ ]]; then
    python create_test_data.py
fi

echo "\n✅ 安裝完成！可執行 ./start_server.sh 啟動服務。"
