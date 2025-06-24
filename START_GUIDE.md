# BlogCommerce 快速啟動指南

## 🚀 一鍵啟動

### 開發模式（推薦）
```bash
./start.sh dev
```
- **統一入口**: http://localhost:8000
- **管理後台**: http://localhost:8000/admin  
- **前端網站**: http://localhost:8000
- 修改前端代碼後使用 `./rebuild.sh` 快速重建

### 熱重載模式（前端密集開發）
```bash
./start.sh hot
```
- **前端開發**: http://localhost:5173 （熱重載）
- **後端 API**: http://localhost:8000

### 生產模式
```bash
./start.sh prod
```
- **統一服務**: http://localhost:8000

### 快速重建（開發模式專用）
```bash
./rebuild.sh
```

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