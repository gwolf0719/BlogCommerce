# Alembic 資料庫遷移

此目錄包含 Alembic 資料庫遷移文件和配置。

## 目錄結構

- `env.py` - Alembic 環境配置文件
- `script.py.mako` - 遷移文件模板
- `versions/` - 遷移文件目錄

## 自動遷移

`start.sh` 腳本會在每次啟動時自動：

1. 檢查 Alembic 配置是否存在
2. 如果沒有遷移文件，自動建立初始遷移
3. 檢查資料庫是否需要更新
4. 執行必要的遷移

## 手動遷移命令

```bash
# 激活虛擬環境
source .venv/bin/activate

# 建立新的遷移文件
python -m alembic revision --autogenerate -m "描述變更"

# 升級到最新版本
python -m alembic upgrade head

# 檢查當前版本
python -m alembic current

# 查看遷移歷史
python -m alembic history
```

## 重要事項

- 每次修改 models 後，都會在下次啟動時自動檢查並建立遷移
- 不需要手動管理 migrations 目錄的內容
- 系統會自動處理初始遷移和後續更新 