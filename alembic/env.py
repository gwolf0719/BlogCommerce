"""
Alembic 環境配置文件
用於配置數據庫遷移環境
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加應用程式路徑到 sys.path
import sys
sys.path.insert(0, os.path.abspath('.'))

# 導入配置和模型
from app.config import settings
from app.database import Base

# 從 models 包中導入所有模型
from app.models import *

# 這是 Alembic Config 物件，提供了 .ini 文件的值
config = context.config

# 設置數據庫 URL 從環境變量或設定中讀取
config.set_main_option("sqlalchemy.url", settings.database_url)

# 解釋配置文件用於 Python 日誌記錄
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加您的模型的 MetaData 物件供 'autogenerate' 支援
target_metadata = Base.metadata

# 其他從 config 中獲取的值，由 env.py 定義
# 可以在此處根據需要獲取多個配置

def run_migrations_offline() -> None:
    """在 'offline' 模式下運行遷移。

    這會配置上下文，只使用 URL 而不是 Engine，
    雖然 Engine 也是可以接受的。
    通過跳過 Engine 的創建，我們甚至不需要 DBAPI 可用。

    調用 context.configure() 和 context.run_migrations() 來
    在沒有 Engine 的情況下運行遷移。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在 'online' 模式下運行遷移。

    在這種情況下，我們需要創建 Engine 
    並將連接與上下文關聯。
    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    # 覆蓋設置中的 URL
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 