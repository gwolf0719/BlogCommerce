import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import base as base_model
from app.models.user import User, UserRole
from app.models.settings import SystemSettings as SettingsModel
from app.config import settings as app_settings
from passlib.context import CryptContext

# 使用與 auth.py 相同的密碼雜湊設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database():
    print("正在初始化資料庫...")
    
    # 建立所有資料表
    base_model.Base.metadata.create_all(bind=engine)
    print("資料表建立完成。")

    db = SessionLocal()
    try:
        # 檢查管理員帳號是否已存在
        admin_user = db.query(User).filter(User.username == app_settings.admin_username).first()
        if not admin_user:
            print(f"正在建立預設管理員帳號: {app_settings.admin_username}")
            hashed_password = pwd_context.hash(app_settings.admin_password)
            new_admin = User(
                username=app_settings.admin_username,
                email=app_settings.admin_email,
                hashed_password=hashed_password,
                full_name=app_settings.admin_full_name,
                is_admin=True,
                is_active=True,
                role=UserRole.ADMIN # 設定為管理員角色
            )
            db.add(new_admin)
            print("管理員帳號建立成功。")
        else:
            print("管理員帳號已存在，跳過建立程序。")

        # 檢查網站設定是否已存在
        site_name_setting = db.query(SettingsModel).filter(SettingsModel.key == "site_name").first()
        if not site_name_setting:
            print("正在建立預設網站設定...")
            default_settings = [
                SettingsModel(key="site_name", value=app_settings.site_name, description="網站名稱", category="general", data_type="string"),
                SettingsModel(key="site_description", value=app_settings.site_description, description="網站描述", category="general", data_type="string"),
                SettingsModel(key="default_currency", value=app_settings.default_currency, description="預設貨幣", category="ecommerce", data_type="string"),
                SettingsModel(key="default_currency_symbol", value=app_settings.default_currency_symbol, description="預設貨幣符號", category="ecommerce", data_type="string"),
            ]
            db.add_all(default_settings)
            print("預設網站設定建立成功。")
        else:
            print("網站設定已存在，跳過建立程序。")

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    print("資料庫初始化與預設資料填充完成。")
