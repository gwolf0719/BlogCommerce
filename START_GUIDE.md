# BlogCommerce 快速啟動指南

## 🚀 統一啟動

使用 `start_server.sh` 腳本來啟動整個應用程式。

```bash
./start_server.sh [PORT]
```

- **[PORT]** (可選): 指定一個 Port，預設為 `8001`。

### 範例

**使用預設 Port (8001):**
```bash
./start_server.sh
```

**使用指定 Port (例如 8080):**
```bash
./start_server.sh 8080
```

### 服務位址

- **網站入口**: `http://localhost:8001` (或您指定的 Port)
- **管理後台**: `http://localhost:8001/admin`

## 📝 預設帳號
- 帳號: `admin`
- 密碼: `admin123456`

## 🛠️ 系統需求
- Node.js 16+
- Python 3.8+
- npm

## 📖 詳細說明
```bash
./start.sh help
``` 