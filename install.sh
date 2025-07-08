#!/bin/bash

# install.sh
# 這個腳本將會設定 BlogCommerce 應用的初始環境

# 發生錯誤時立即停止
set -e

# 專案根目錄
PROJECT_ROOT=$(pwd)

# 虛擬環境目錄
VENV_DIR="$PROJECT_ROOT/.venv"

# --- 函式定義 ---

# 顯示資訊
info() {
    echo "[INFO] $1"
}

# 顯示錯誤並退出
die() {
    echo "[ERROR] $1" >&2
    exit 1
}

# --- 主要邏輯 ---

# 1. 檢查並設定 Python 虛擬環境
if [ ! -d "$VENV_DIR" ]; then
    info "正在建立 Python 虛擬環境於 $VENV_DIR ..."
    python3 -m venv "$VENV_DIR" || die "建立虛擬環境失敗。請確認您已安裝 python3 和 venv。"
else
    info "虛擬環境已存在。"
fi

# 啟用虛擬環境
source "$VENV_DIR/bin/activate"
info "已啟用虛擬環境。"

# 2. 升級 pip
info "正在升級 pip..."
python3 -m pip install --upgrade pip

# 3. 安裝 Python 依賴
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    info "正在安裝 requirements.txt 中的依賴..."
    pip install -r "$PROJECT_ROOT/requirements.txt" || die "安裝 Python 依賴失敗。"
    info "Python 依賴安裝完成。"
else
    die "找不到 requirements.txt 檔案。"
fi

# 3. 設定 .env 環境變數檔案
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    info "正在從 .env.example 建立 .env 檔案..."
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    else
        die "找不到 .env.example 範本檔案。"
    fi

    info "開始設定資料庫連線..."
    echo "請選擇您要使用的資料庫類型:"
    echo "  1) SQLite (預設，最簡單)"
    echo "  2) PostgreSQL"
    echo "  3) MySQL"
    read -p "請輸入選項 [1-3]: " DB_CHOICE

    case $DB_CHOICE in
        2)
            info "您選擇了 PostgreSQL。"
            read -p "請輸入資料庫主機 [localhost]: " DB_HOST
            DB_HOST=${DB_HOST:-localhost}
            read -p "請輸入資料庫通訊埠 [5432]: " DB_PORT
            DB_PORT=${DB_PORT:-5432}
            read -p "請輸入資料庫名稱: " DB_NAME
            read -p "請輸入資料庫使用者名稱: " DB_USER
            read -s -p "請輸入資料庫密碼: " DB_PASSWORD
            echo
            DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
            sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL="${DATABASE_URL}"|" "$PROJECT_ROOT/.env"
            ;;
        3)
            info "您選擇了 MySQL。"
            read -p "請輸入資料庫主機 [localhost]: " DB_HOST
            DB_HOST=${DB_HOST:-localhost}
            read -p "請輸入資料庫通訊埠 [3306]: " DB_PORT
            DB_PORT=${DB_PORT:-3306}
            read -p "請輸入資料庫名稱: " DB_NAME
            read -p "請輸入資料庫使用者名稱: " DB_USER
            read -s -p "請輸入資料庫密碼: " DB_PASSWORD
            echo
            DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
            sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL="${DATABASE_URL}"|" "$PROJECT_ROOT/.env"
            ;;
        *)
            info "您選擇了 SQLite (預設)。"
            DATABASE_URL="sqlite:///./blogcommerce.db"
            sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL="${DATABASE_URL}"|" "$PROJECT_ROOT/.env"
            ;;
    esac
    info ".env 中的 DATABASE_URL 已更新。"

    info "開始設定管理員帳號資訊..."
    read -p "請輸入管理員帳號 (預設為 'admin'): " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}
    sed -i.bak "s|^ADMIN_USERNAME=.*|ADMIN_USERNAME="${ADMIN_USER}"|" "$PROJECT_ROOT/.env"
    info ".env 中的 ADMIN_USERNAME 已更新。"

    read -p "請輸入管理員電子郵件 (預設為 'admin@example.com'): " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@example.com}
    sed -i.bak "s|^ADMIN_EMAIL=.*|ADMIN_EMAIL="${ADMIN_EMAIL}"|" "$PROJECT_ROOT/.env"
    info ".env 中的 ADMIN_EMAIL 已更新。"

    read -p "請輸入管理員全名 (預設為 '系統管理員'): " ADMIN_FULL_NAME
    ADMIN_FULL_NAME=${ADMIN_FULL_NAME:-"系統管理員"}
    sed -i.bak "s|^ADMIN_FULL_NAME=.*|ADMIN_FULL_NAME="${ADMIN_FULL_NAME}"|" "$PROJECT_ROOT/.env"
    info ".env 中的 ADMIN_FULL_NAME 已更新。"

    read -s -p "請輸入管理員密碼 (預設為 'admin123456'): " ADMIN_PASS
    ADMIN_PASS=${ADMIN_PASS:-admin123456}
    echo
    sed -i.bak "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD="${ADMIN_PASS}"|" "$PROJECT_ROOT/.env"
    info ".env 中的 ADMIN_PASSWORD 已更新。"

else
    info ".env 檔案已存在，跳過建立與設定程序。"
fi

# 4. 執行資料庫遷移 (如果有的話)
# 注意：此專案目前使用 create_all。如果未來導入 Alembic，請取消註解以下程式碼
# info "正在執行資料庫遷移..."
# alembic upgrade head || die "資料庫遷移失敗。"
# info "資料庫遷移完成。"

# 5. 執行資料庫填充腳本
info "正在執行資料庫填充腳本以建立預設資料..."
python "$PROJECT_ROOT/seed_database.py" || die "資料庫填充失敗。"
info "資料庫填充完成。"

# --- 前端設定 ---

if [ -d "$PROJECT_ROOT/admin-src" ]; then
    info "偵測到前端目錄，開始設定前端環境..."
    cd "$PROJECT_ROOT/admin-src" || die "無法進入 admin-src 目錄。"

    # 6. 安裝 Node.js 依賴
    if [ -f "package.json" ]; then
        info "正在安裝 Node.js 依賴 (npm install)..."
        npm install || die "npm install 失敗。請確認您已安裝 Node.js 和 npm。"
        info "Node.js 依賴安裝完成。"
    else
        info "找不到 package.json，跳過 npm install。"
    fi

    cd "$PROJECT_ROOT"
fi


# --- 完成 ---

cat <<'EOF'

=========================================================
 BlogCommerce 環境設定完成！
=========================================================

下一步:

1.  **檢查並編輯 `.env` 檔案**:
    請開啟 `.env` 檔案，並根據您的需求修改資料庫連線、郵件伺服器等設定。
    特別注意 `DATABASE_URL` 和 `ADMIN_PASSWORD`。

2.  **啟動後端伺服器**:
    source .venv/bin/activate
    ./start_server.sh

3.  **啟動前端開發伺服器**:
    cd admin-src
    npm run dev

感謝您的使用！
EOF
