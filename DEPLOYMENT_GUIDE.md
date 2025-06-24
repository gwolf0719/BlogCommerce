# BlogCommerce 部署指南

本指南將引導您完成 BlogCommerce 系統的完整部署過程，包括開發環境、測試環境和生產環境的設置。

---

## 📋 系統需求

### 最低需求
- **作業系統**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.9+
- **Node.js**: 16.0+
- **記憶體**: 4GB RAM
- **儲存空間**: 10GB 可用空間
- **資料庫**: SQLite (開發) / PostgreSQL (生產)

### 推薦配置
- **CPU**: 4 核心以上
- **記憶體**: 8GB RAM
- **儲存空間**: 50GB SSD
- **網路**: 穩定的網際網路連線

---

## 🚀 快速部署 (開發環境)

### 1. 下載專案
```bash
git clone <repository-url>
cd BlogCommerce
```

### 2. 設置 Python 虛擬環境
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 設置環境變數
```bash
cp .env.example .env
# 編輯 .env 檔案設置必要參數
```

### 5. 初始化資料庫
```bash
python init_db.py
python init_settings.py
```

### 6. 創建測試資料
```bash
python create_test_data.py
```

### 7. 啟動服務
```bash
python run.py
```

### 8. 前端構建 (可選)
```bash
cd frontend
npm install
npm run build
```

**訪問應用**: http://localhost:8000

---

## 🔧 詳細部署步驟

### 環境變數設置

創建 `.env` 檔案：

```bash
# 應用設置
DEBUG=True
SECRET_KEY=your-secret-key-here
SITE_NAME=BlogCommerce
SITE_DESCRIPTION=Your Blog Commerce Site

# 資料庫設置
DATABASE_URL=sqlite:///./app.db

# 安全設置
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# 分頁設置
POSTS_PER_PAGE=10
PRODUCTS_PER_PAGE=12
ORDERS_PER_PAGE=20

# 郵件設置 (可選)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AI 功能設置 (可選)
OPENAI_API_KEY=your-openai-api-key
```

### 資料庫配置

#### SQLite (開發環境)
預設使用 SQLite，無需額外配置。

#### PostgreSQL (生產環境)
```bash
# 安裝 PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# 創建資料庫
sudo -u postgres createuser --interactive
sudo -u postgres createdb blogcommerce

# 更新 .env
DATABASE_URL=postgresql://username:password@localhost/blogcommerce
```

---

## 🐳 Docker 部署

### 使用 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/blogcommerce
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: blogcommerce
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 部署命令
```bash
docker-compose up -d
```

---

## ☁️ 雲端部署

### Heroku 部署

1. **安裝 Heroku CLI**
```bash
# 下載並安裝 Heroku CLI
```

2. **創建 Heroku 應用**
```bash
heroku create your-app-name
```

3. **設置環境變數**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
```

4. **部署應用**
```bash
git push heroku main
```

5. **初始化資料庫**
```bash
heroku run python init_db.py
heroku run python init_settings.py
```

### AWS EC2 部署

1. **啟動 EC2 實例**
   - 選擇 Ubuntu 20.04 LTS
   - 配置安全群組 (開放 80, 443, 22 端口)

2. **連線到實例**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **安裝依賴**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql
```

4. **部署應用**
```bash
git clone <your-repo>
cd BlogCommerce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **設置 Nginx**
```nginx
# /etc/nginx/sites-available/blogcommerce
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔒 安全設置

### SSL/TLS 證書
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 防火牆設置
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 安全標頭
在 Nginx 中添加：
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
```

---

## 📊 監控與日誌

### 日誌設置
應用日誌位於 `logs/` 目錄：
- `app.log` - 應用程式日誌
- `error.log` - 錯誤日誌
- `access.log` - 訪問日誌

### 系統監控
```bash
# 安裝監控工具
pip install psutil

# 運行健康檢查
python system_health_check.py
```

### 備份策略
```bash
# 資料庫備份
pg_dump blogcommerce > backup_$(date +%Y%m%d).sql

# 文件備份
tar -czf files_backup_$(date +%Y%m%d).tar.gz app/static/uploads
```

---

## 🔄 維護操作

### 更新應用
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
# 重啟服務
```

### 資料庫遷移
```bash
# 備份現有資料
python backup_db.py

# 應用遷移
python migrate_db.py
```

### 效能優化
```bash
# 清理舊日誌
find logs/ -name "*.log" -mtime +30 -delete

# 優化資料庫
python optimize_db.py
```

---

## 🐛 故障排除

### 常見問題

#### 1. 應用無法啟動
```bash
# 檢查日誌
tail -f logs/app.log

# 檢查端口佔用
netstat -tlnp | grep :8000
```

#### 2. 資料庫連線失敗
```bash
# 檢查資料庫狀態
sudo systemctl status postgresql

# 測試連線
python -c "from app.database import get_db; print('DB OK')"
```

#### 3. 靜態文件無法載入
```bash
# 檢查文件權限
ls -la app/static/

# 重新收集靜態文件
python collect_static.py
```

### 日誌分析
```bash
# 查看錯誤統計
grep "ERROR" logs/app.log | wc -l

# 分析慢查詢
grep "slow" logs/app.log
```

---

## 📞 支援資訊

### 系統狀態檢查
訪問 `/health` 端點檢查系統狀態

### 文件資源
- [API 文件](./API_DOCUMENTATION.md)
- [功能驗證清單](./功能驗證待辦清單.md)
- [測試報告](./TESTING_REPORT.md)

### 聯絡資訊
- **技術支援**: [您的聯絡資訊]
- **文件更新**: [GitHub Issues]

---

**最後更新**: 2024-12-19  
**版本**: 1.0.0  
**狀態**: ✅ 生產就緒 