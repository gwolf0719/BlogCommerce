# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

# 將前端程式碼放在 /usr/src/app/admin-src
WORKDIR /usr/src/app/admin-src

# 複製 package files 並安裝依賴
# 使用 npm ci 以確保使用 package-lock.json 的精確版本
COPY admin-src/package*.json ./
RUN npm ci

# 複製源代碼並構建
COPY admin-src/ .
RUN npm run build

# --- 除錯步驟 ---
# 在建置後列出工作目錄的內容，以確認建置結果
RUN echo "--- Contents of /usr/src/app/admin-src after build ---" && ls -la
RUN echo "--- Contents of /usr/src/app/admin (build output) ---" && ls -la ../admin

# Stage 2: Build backend dependencies
FROM python:3.10-slim AS backend-builder

WORKDIR /usr/src/app

# 安裝構建依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 3: Production image
FROM python:3.10-slim

# 將工作目錄更改為 /usr/src/app，以避免與掛載點衝突
WORKDIR /usr/src/app

# 安裝運行時依賴
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# 複製 Python 依賴
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 複製應用程式代碼到新的工作目錄
COPY app/ ./app/

# 複製前端構建結果
COPY --from=frontend-builder /usr/src/app/admin/ ./admin/

# 創建上傳目錄，這個目錄將會被 NFS 掛載點覆蓋
# 我們仍然在映像檔中創建它，以確保在沒有掛載的情況下路徑依然存在
RUN mkdir -p /usr/src/app/app/static/uploads && \
    chown -R appuser:appuser /usr/src/app

# 設定環境變數，更新 PYTHONPATH
ENV PYTHONPATH=/usr/src/app
ENV PORT=8080
ENV ENV=production

# 暴露端口
EXPOSE 8080

# 啟動應用程式
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
