#!/usr/bin/env python3
import os
import re
import asyncio
import subprocess

from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash
from sqlalchemy.orm import Session
from app.config import settings

# 清理 MAX_FILE_SIZE 環境變數中的註解
max_file_size_env = os.getenv("MAX_FILE_SIZE")
if max_file_size_env:
    os.environ["MAX_FILE_SIZE"] = re.sub(r'\s*#.*', '', max_file_size_env).strip()

def run_alembic_upgrade():
    """執行 alembic migrate 到最新版本"""
    print("Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during database migration: {e}")
        exit(1)

def check_admin_exists(db: Session) -> bool:
    """檢查是否已有管理員帳號"""
    return db.query(User).filter(User.is_admin == True).first() is not None

def create_admin_user(db: Session):
    """從設定檔建立預設管理員帳號"""
    print("No admin user found. Creating one from config...")
    username = settings.admin_username
    email = settings.admin_email
    password = settings.admin_password

    # 避免重複建立
    if db.query(User).filter(User.username == username).first():
        print(f"Admin user with username '{username}' already exists.")
        return
    if db.query(User).filter(User.email == email).first():
        print(f"Admin user with email '{email}' already exists.")
        return

    # 使用官方 bcrypt 產生密碼雜湊
    hashed_password = get_password_hash(password)

    admin_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print("Admin user created successfully.")

async def main():
    """主流程：先跑 migration，再建立管理員"""
    run_alembic_upgrade()

    db = SessionLocal()
    try:
        if not check_admin_exists(db):
            create_admin_user(db)
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
