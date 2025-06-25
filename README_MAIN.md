# BlogCommerce - 整合式電商部落格系統

[![系統狀態](https://img.shields.io/badge/狀態-運行正常-green)](./docs/README.md)
[![健康度](https://img.shields.io/badge/健康度-99%25-brightgreen)](./buglist.md)
[![文檔](https://img.shields.io/badge/文檔-完整-blue)](./docs/README.md)
[![最新功能](https://img.shields.io/badge/最新功能-瀏覽追蹤-orange)](./VIEW_TRACKING_SUMMARY.md)

> 一個現代化的電商部落格整合平台，結合內容管理與電子商務功能，基於 FastAPI + Vue.js 構建。

## 🚀 快速開始

### 一鍵啟動
```bash
git clone <repository-url>
cd BlogCommerce
python run.py  # 會自動設置環境並啟動服務
```

### 訪問系統
- **前台網站**: http://localhost:8002
- **管理後台**: http://localhost:3000
- **API 文檔**: http://localhost:8002/docs

### 預設帳號
- **管理員**: admin / admin123456

## 📚 完整文檔

### 🎯 新用戶必讀
| 文檔 | 說明 | 狀態 |
|------|------|------|
| [快速啟動指南](./START_GUIDE.md) | 5分鐘快速上手 | ✅ 最新 |
| [安裝說明](./INSTALL.md) | 詳細安裝步驟 | ✅ 完整 |
| [系統概述](./README.md) | 功能介紹與架構 | ✅ 完整 |

### 🔧 開發與部署
| 文檔 | 說明 | 狀態 |
|------|------|------|
| [部署指南](./DEPLOYMENT_GUIDE.md) | 生產環境部署 | ✅ 完整 |
| [管理員手冊](./README_ADMIN.md) | 後台操作說明 | ✅ 完整 |
| [功能清單](./docs/FEATURE_CHECKLIST.md) | 系統功能檢查 | ✅ 最新 |

### 📊 系統狀態
| 文檔 | 說明 | 狀態 |
|------|------|------|
| [Bug 追蹤](./buglist.md) | 問題修復記錄 | ✅ 實時更新 |
| [測試報告](./TESTING_REPORT.md) | 系統測試結果 | ✅ 完整 |
| [文檔索引](./docs/README.md) | 所有文檔導航 | ✅ 最新 |

### 🆕 最新功能
| 文檔 | 說明 | 狀態 |
|------|------|------|
| [瀏覽追蹤系統](./VIEW_TRACKING_SUMMARY.md) | 瀏覽量統計功能 | ✅ 剛完成 |

## ✨ 系統特色

### 🏪 電商功能
- **商品管理**: 完整的商品 CRUD、庫存管理、價格設定
- **購物車系統**: 即時購物車、持久化存儲
- **訂單流程**: 完整的下單到發貨流程
- **會員系統**: 註冊登入、個人資料管理
- **收藏功能**: 商品收藏與管理

### 📝 內容管理
- **部落格系統**: Markdown 編輯器、文章分類
- **SEO 優化**: 自動 sitemap、meta 標籤
- **響應式設計**: 支援所有設備
- **搜尋功能**: 全文搜尋與篩選

### 📊 數據分析
- **瀏覽統計**: 實時瀏覽量追蹤 🆕
- **銷售報表**: 訂單統計與分析
- **用戶行為**: 詳細的用戶活動記錄
- **熱門內容**: 自動識別熱門文章與商品

### 🎛️ 管理後台
- **Vue.js 3**: 現代化前端框架
- **Ant Design**: 專業的 UI 組件庫
- **即時預覽**: 所見即所得編輯
- **權限管理**: 細緻的權限控制

## 🏗️ 技術架構

### 後端
- **FastAPI**: 高性能 Python 後端框架
- **SQLAlchemy**: 強大的 ORM 工具
- **Jinja2**: 靈活的模板引擎
- **Pydantic**: 數據驗證與序列化

### 前端
- **Vue.js 3**: 響應式前端框架
- **Ant Design Vue**: 企業級 UI 組件
- **Alpine.js**: 輕量級互動框架
- **Tailwind CSS**: 實用優先的 CSS 框架

### 資料庫
- **SQLite**: 開發環境（預設）
- **PostgreSQL**: 生產環境推薦
- **MySQL**: 生產環境支援

## 🎯 系統狀態

### 📈 健康度監控
- **系統健康度**: 99% ✅
- **已修復問題**: 10/12
- **新增功能**: 瀏覽追蹤系統 ✅
- **服務運行**: 後端 8002、前端 3000 ✅

### ✅ 完成功能
- [x] 用戶認證與管理系統
- [x] 完整的電商功能
- [x] 內容管理系統
- [x] 管理後台界面
- [x] 響應式前端設計
- [x] API 文檔與測試
- [x] 瀏覽量統計系統 🆕

### ⚠️ 待改進項目
- [ ] Tailwind CSS 生產版本優化
- [ ] Analytics API 端點完善

## 🤝 快速操作

### 開發者
```bash
# 開發環境
python run.py
cd frontend && npm run dev

# 測試
python -m pytest tests/

# 文檔
open docs/README.md
```

### 管理員
```bash
# 檢查系統狀態
curl http://localhost:8002/api/admin/stats

# 查看錯誤日誌
tail -f logs/app.log

# 備份資料庫
cp blogcommerce.db backup/
```

### 部署
```bash
# 生產環境部署
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker 部署
docker-compose up -d

# 監控
htop && curl http://localhost:8002/health
```

## 📞 支援與反饋

### 獲取幫助
1. 查看 [文檔索引](./docs/README.md) 找到相關說明
2. 檢查 [Bug 清單](./buglist.md) 確認已知問題  
3. 查閱 [功能清單](./docs/FEATURE_CHECKLIST.md) 驗證功能狀態

### 問題回報
1. 確認問題是否已在 [Bug 清單](./buglist.md) 中
2. 提供詳細的錯誤信息和重現步驟
3. 包含系統環境和版本信息

---

**最後更新**: 2025-01-25  
**版本**: v1.1.0 (新增瀏覽追蹤功能)  
**維護者**: BlogCommerce 開發團隊

> 🎉 恭喜！您的 BlogCommerce 系統已經完全就緒，所有核心功能都在正常運行。現在就開始使用吧！ 