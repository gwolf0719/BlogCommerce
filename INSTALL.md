# 📋 BlogCommerce 完整安裝指南

本指南將協助您從零開始建立 BlogCommerce 部落格電商平台，包含開發環境和生產環境的完整設定。

---

## 📋 目錄

1. [系統需求](#系統需求)
2. [開發環境安裝](#開發環境安裝)
3. [生產環境部署](#生產環境部署)
4. [Apache 配置](#apache-配置)
5. [Nginx 配置](#nginx-配置)
6. [SSL 憑證設定](#ssl-憑證設定)
7. [資料庫設定](#資料庫設定)
8. [故障排除](#故障排除)

---

## 🔧 系統需求

### 最低需求
- **作業系統**：Linux (Ubuntu 20.04+)、macOS 10.15+、Windows 10+
- **Python**：3.8 或以上版本
- **記憶體**：最少 512MB（建議 2GB 以上）
- **硬碟空間**：最少 1GB
- **網路**：需要網際網路連線下載套件

### 推薦需求
- **作業系統**：Ubuntu 22.04 LTS 或 CentOS 8+
- **Python**：3.11+
- **記憶體**：4GB 以上
- **硬碟空間**：10GB 以上（含日誌和備份）
- **處理器**：2 核心以上
- **瀏覽器**：支援 JavaScript 的現代瀏覽器（用於流量追蹤）

---

## 🚀 開發環境安裝

### 步驟 1：系統準備

#### Ubuntu/Debian 系統
```bash
# 更新系統套件
sudo apt update && sudo apt upgrade -y

# 安裝必要套件
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip

# 安裝 Node.js（如需前端開發）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安裝資料庫（可選）
sudo apt install -y sqlite3 mysql-server postgresql
```

#### CentOS/RHEL 系統
```bash
# 更新系統套件
sudo yum update -y

# 安裝 EPEL 倉庫
sudo yum install -y epel-release

# 安裝必要套件
sudo yum install -y python3 python3-pip git curl wget unzip

# 安裝 Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安裝資料庫
sudo yum install -y sqlite mysql-server postgresql-server
```

#### macOS 系統
```bash
# 安裝 Homebrew（如未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝 Python 和相關工具
brew install python3 git

# 安裝資料庫（可選）
brew install sqlite mysql postgresql
```

#### Windows 系統
1. 下載並安裝 [Python](https://www.python.org/downloads/windows/)
2. 下載並安裝 [Git](https://git-scm.com/download/win)
3. 開啟 PowerShell 或 CMD 執行後續命令

### 步驟 2：複製專案

```bash
# 複製專案（請替換為實際的 Git 倉庫地址）
git clone https://github.com/your-username/blogcommerce.git
cd blogcommerce

# 或者如果您有專案壓縮檔
wget https://example.com/blogcommerce.zip
unzip blogcommerce.zip
cd blogcommerce
```

### 步驟 3：設定虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 升級 pip
pip install --upgrade pip
```

### 步驟 4：安裝相依套件

```bash
# 安裝 Python 套件
pip install -r requirements.txt

# 如果遇到相依性問題，可以逐一安裝
pip install fastapi uvicorn sqlalchemy alembic pydantic
pip install python-multipart jinja2 python-jose passlib
pip install email-validator python-dotenv httpx pytest
```

### 步驟 5：環境設定

```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯環境變數（使用您偏好的編輯器）
nano .env
# 或者
vim .env
# 或者
code .env
```

**重要環境變數設定：**
```bash
# 基本設定
SITE_NAME=BlogCommerce
SITE_DESCRIPTION=部落格與電商整合平台
DEBUG=True
SECRET_KEY=your-super-secret-key-here

# 資料庫設定
DATABASE_URL=sqlite:///./blogcommerce.db

# JWT 設定
JWT_SECRET_KEY=your-jwt-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 管理員帳號
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123456
```

### 步驟 6：初始化資料庫

```bash
# 初始化資料庫結構
python init_db.py

# 建立測試資料（可選）
python create_test_data.py
```

### 步驟 7：啟動開發服務器

```bash
# 啟動應用程式
./start_server.sh

# 或者使用 uvicorn (如果不想自動建置前端)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步驟 8：驗證安裝

開啟瀏覽器訪問：
- **前台網站**：http://localhost:8000
- **管理後台**：http://localhost:8000/admin/login
- **API 文檔**：http://localhost:8000/docs

---

## 🌐 生產環境部署

### 步驟 1：生產環境準備

```bash
# 建立應用程式使用者
sudo adduser blogcommerce
sudo usermod -aG sudo blogcommerce

# 切換到應用程式使用者
sudo su - blogcommerce

# 建立應用程式目錄
mkdir -p /home/blogcommerce/apps
cd /home/blogcommerce/apps
```

### 步驟 2：部署應用程式

```bash
# 複製專案檔案
git clone https://github.com/your-username/blogcommerce.git
cd blogcommerce

# 設定虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt
pip install gunicorn
```

### 步驟 3：生產環境設定

```bash
# 設定生產環境變數
cp .env.example .env
nano .env
```

**生產環境變數範例：**
```bash
# 基本設定
SITE_NAME=BlogCommerce
SITE_DESCRIPTION=部落格與電商整合平台
SITE_URL=https://yourdomain.com
DEBUG=False
SECRET_KEY=your-production-secret-key

# 資料庫設定（建議使用 PostgreSQL 或 MySQL）
DATABASE_URL=postgresql://username:password@localhost:5432/blogcommerce

# JWT 設定
JWT_SECRET_KEY=your-production-jwt-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 管理員帳號
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-admin-password
```

### 步驟 4：建立系統服務

建立 systemd 服務檔案：

```bash
sudo nano /etc/systemd/system/blogcommerce.service
```

**服務檔案內容：**
```ini
[Unit]
Description=BlogCommerce Web Application
After=network.target

[Service]
Type=exec
User=blogcommerce
Group=blogcommerce
WorkingDirectory=/home/blogcommerce/apps/blogcommerce
Environment=PATH=/home/blogcommerce/apps/blogcommerce/venv/bin
ExecStart=/home/blogcommerce/apps/blogcommerce/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟動服務
sudo systemctl start blogcommerce

# 設定開機自動啟動
sudo systemctl enable blogcommerce

# 檢查服務狀態
sudo systemctl status blogcommerce
```

---

## 🌐 Apache 配置

### 安裝 Apache

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```

#### CentOS/RHEL
```bash
sudo yum install -y httpd
sudo systemctl start httpd
sudo systemctl enable httpd
```

### 配置 Apache 虛擬主機

建立虛擬主機配置檔案：

```bash
sudo nano /etc/apache2/sites-available/blogcommerce.conf
```

**Apache 配置檔案：**
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    DocumentRoot /home/blogcommerce/apps/blogcommerce/app/static
    
    # 代理設定
    ProxyPreserveHost On
    ProxyRequests Off
    
    # 靜態檔案直接由 Apache 提供
    Alias /static /home/blogcommerce/apps/blogcommerce/app/static
    <Directory /home/blogcommerce/apps/blogcommerce/app/static>
        Require all granted
    </Directory>
    
    # API 和動態內容代理到 FastAPI
    ProxyPass /static !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # 日誌設定
    ErrorLog ${APACHE_LOG_DIR}/blogcommerce_error.log
    CustomLog ${APACHE_LOG_DIR}/blogcommerce_access.log combined
    
    # 安全標頭
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
```

**啟用網站和模組：**
```bash
# 啟用必要模組
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod rewrite

# 啟用網站
sudo a2ensite blogcommerce.conf
sudo a2dissite 000-default.conf

# 測試配置
sudo apache2ctl configtest

# 重新啟動 Apache
sudo systemctl restart apache2
```

### Apache SSL 配置（HTTPS）

```bash
# 啟用 SSL 模組
sudo a2enmod ssl

# 建立 SSL 虛擬主機
sudo nano /etc/apache2/sites-available/blogcommerce-ssl.conf
```

**SSL 配置檔案：**
```apache
<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    DocumentRoot /home/blogcommerce/apps/blogcommerce/app/static
    
    # SSL 設定
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/yourdomain.com.crt
    SSLCertificateKeyFile /etc/ssl/private/yourdomain.com.key
    
    # 代理設定
    ProxyPreserveHost On
    ProxyRequests Off
    
    # 靜態檔案
    Alias /static /home/blogcommerce/apps/blogcommerce/app/static
    <Directory /home/blogcommerce/apps/blogcommerce/app/static>
        Require all granted
    </Directory>
    
    # 代理到 FastAPI
    ProxyPass /static !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # 安全標頭
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    # 日誌
    ErrorLog ${APACHE_LOG_DIR}/blogcommerce_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/blogcommerce_ssl_access.log combined
</VirtualHost>

# 重新導向 HTTP 到 HTTPS
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>
```

---

## 🔧 Nginx 配置

### 安裝 Nginx

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### CentOS/RHEL
```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 配置 Nginx

建立網站配置檔案：

```bash
sudo nano /etc/nginx/sites-available/blogcommerce
```

**Nginx 配置檔案：**
```nginx
# HTTP 配置（重新導向到 HTTPS）
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 憑證設定
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    # SSL 安全設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全標頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 靜態檔案處理
    location /static/ {
        alias /home/blogcommerce/apps/blogcommerce/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 上傳檔案處理
    location /uploads/ {
        alias /home/blogcommerce/apps/blogcommerce/app/static/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到 FastAPI 應用程式
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支援（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超時設定
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Gzip 壓縮
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 日誌設定
    access_log /var/log/nginx/blogcommerce_access.log;
    error_log /var/log/nginx/blogcommerce_error.log;
}
```

**啟用網站：**
```bash
# 測試配置
sudo nginx -t

# 建立符號連結（Ubuntu/Debian）
sudo ln -s /etc/nginx/sites-available/blogcommerce /etc/nginx/sites-enabled/

# 移除預設網站
sudo rm /etc/nginx/sites-enabled/default

# 重新啟動 Nginx
sudo systemctl restart nginx
```

### Nginx 負載平衡配置（多個應用程式實例）

```nginx
# 上游服務器設定
upstream blogcommerce_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 和其他設定...
    
    location / {
        proxy_pass http://blogcommerce_backend;
        # 其他代理設定...
    }
}
```

---

## 🔐 SSL 憑證設定

### 使用 Let's Encrypt 免費 SSL 憑證

#### 安裝 Certbot

**Ubuntu/Debian：**
```bash
sudo apt install -y certbot python3-certbot-nginx
# 或者使用 Apache
sudo apt install -y certbot python3-certbot-apache
```

**CentOS/RHEL：**
```bash
sudo yum install -y certbot python3-certbot-nginx
# 或者使用 Apache
sudo yum install -y certbot python3-certbot-apache
```

#### 取得 SSL 憑證

**使用 Nginx：**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**使用 Apache：**
```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

**手動模式：**
```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

#### 自動更新憑證

```bash
# 測試自動更新
sudo certbot renew --dry-run

# 設定 cron 工作自動更新
sudo crontab -e

# 加入以下行（每日檢查更新）
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 💾 資料庫設定

### SQLite（預設，適合小型網站）

```bash
# SQLite 已包含在 Python 中，無需額外安裝
# 在 .env 檔案中設定
DATABASE_URL=sqlite:///./blogcommerce.db
```

### PostgreSQL（推薦用於生產環境）

#### 安裝 PostgreSQL

**Ubuntu/Debian：**
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**CentOS/RHEL：**
```bash
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 設定 PostgreSQL

```bash
# 切換到 postgres 使用者
sudo -u postgres psql

# 在 PostgreSQL 提示符中執行
CREATE DATABASE blogcommerce;
CREATE USER blogcommerce WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE blogcommerce TO blogcommerce;
\q
```

**在 .env 檔案中設定：**
```bash
DATABASE_URL=postgresql://blogcommerce:your_password@localhost:5432/blogcommerce
```

### MySQL（備選方案）

#### 安裝 MySQL

**Ubuntu/Debian：**
```bash
sudo apt install -y mysql-server
sudo mysql_secure_installation
```

**CentOS/RHEL：**
```bash
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
sudo mysql_secure_installation
```

#### 設定 MySQL

```bash
# 登入 MySQL
sudo mysql -u root -p

# 在 MySQL 提示符中執行
CREATE DATABASE blogcommerce;
CREATE USER 'blogcommerce'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blogcommerce.* TO 'blogcommerce'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**在 .env 檔案中設定：**
```bash
DATABASE_URL=mysql+pymysql://blogcommerce:your_password@localhost:3306/blogcommerce
```

---

## 🔧 高級配置

### 使用 Redis 做快取

#### 安裝 Redis

```bash
# Ubuntu/Debian
sudo apt install -y redis-server

# CentOS/RHEL
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### 配置快取

在 .env 檔案中加入：
```bash
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300
```

### 檔案上傳設定

```bash
# 建立上傳目錄
mkdir -p /home/blogcommerce/apps/blogcommerce/app/static/uploads
chown -R blogcommerce:blogcommerce /home/blogcommerce/apps/blogcommerce/app/static/uploads

# 設定權限
chmod 755 /home/blogcommerce/apps/blogcommerce/app/static/uploads
```

### 日誌管理

建立日誌輪轉設定：

```bash
sudo nano /etc/logrotate.d/blogcommerce
```

```
/home/blogcommerce/apps/blogcommerce/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 blogcommerce blogcommerce
    postrotate
        systemctl reload blogcommerce
    endscript
}
```

### 備份設定

建立備份腳本：

```bash
nano /home/blogcommerce/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/blogcommerce/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 建立備份目錄
mkdir -p $BACKUP_DIR

# 備份資料庫（SQLite）
cp /home/blogcommerce/apps/blogcommerce/blogcommerce.db $BACKUP_DIR/blogcommerce_$DATE.db

# 備份上傳檔案
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /home/blogcommerce/apps/blogcommerce/app/static/uploads

# 刪除 30 天前的備份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

設定定期備份：
```bash
chmod +x /home/blogcommerce/backup.sh
crontab -e

# 加入每日備份
0 2 * * * /home/blogcommerce/backup.sh
```

---

## 🚨 故障排除

### 常見問題

#### 1. 應用程式無法啟動

**檢查步驟：**
```bash
# 檢查服務狀態
sudo systemctl status blogcommerce

# 查看日誌
sudo journalctl -u blogcommerce -f

# 檢查端口占用
sudo netstat -tlnp | grep 8000

# 手動測試啟動
cd /home/blogcommerce/apps/blogcommerce
source venv/bin/activate
python run.py
```

#### 2. 靜態檔案無法載入

**檢查步驟：**
```bash
# 檢查檔案權限
ls -la /home/blogcommerce/apps/blogcommerce/app/static/

# 檢查 Web 服務器配置
sudo nginx -t
# 或者
sudo apache2ctl configtest
```

#### 3. 資料庫連線問題

**檢查步驟：**
```bash
# 檢查資料庫服務
sudo systemctl status postgresql
# 或者
sudo systemctl status mysql

# 測試資料庫連線
python3 -c "from app.database import engine; print('Database connection successful')"
```

#### 4. SSL 憑證問題

**檢查步驟：**
```bash
# 檢查憑證有效性
sudo certbot certificates

# 測試 SSL 配置
openssl s_client -connect yourdomain.com:443
```

### 效能調整

#### 1. Gunicorn 調整

```bash
# 在 systemd 服務檔案中調整 worker 數量
ExecStart=/home/blogcommerce/apps/blogcommerce/venv/bin/gunicorn app.main:app -w 8 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

#### 2. 資料庫調整

**PostgreSQL 調整：**
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf

# 調整以下參數
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

#### 3. Web 服務器調整

**Nginx 調整：**
```nginx
# 在 nginx.conf 中調整
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 10M;
```

---

## 📞 技術支援

如果您在安裝過程中遇到問題：

1. **檢查日誌檔案**：查看應用程式、Web 服務器和系統日誌
2. **確認服務狀態**：使用 `systemctl status` 檢查各項服務
3. **網路測試**：使用 `curl` 或 `wget` 測試 API 端點
4. **權限檢查**：確認檔案和目錄權限正確設定

---

**🎉 恭喜！您已成功安裝 BlogCommerce 系統！**

現在您可以開始使用這個功能完整的部落格電商平台了。記得定期更新系統和進行備份，以確保系統安全和資料完整性。 