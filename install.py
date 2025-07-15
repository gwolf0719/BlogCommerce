
import os
import re

# Clean up the MAX_FILE_SIZE environment variable
max_file_size_env = os.getenv("MAX_FILE_SIZE")
if max_file_size_env:
    os.environ["MAX_FILE_SIZE"] = re.sub(r'\s*#.*', '', max_file_size_env).strip()

import asyncio
import subprocess
from getpass import getpass
from app.database import SessionLocal, engine
from app.models.user import User
from app.auth import get_password_hash
from sqlalchemy.orm import Session

def run_alembic_upgrade():
    """Runs the alembic upgrade head command."""
    print("Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during database migration: {e}")
        exit(1)

def check_admin_exists(db: Session):
    """Checks if an admin user already exists in the database."""
    return db.query(User).filter(User.is_admin == True).first() is not None

from app.config import settings

def create_admin_user(db: Session):
    """Creates a new admin user from config."""
    print("No admin user found. Creating one from config...")
    username = settings.admin_username
    email = settings.admin_email
    password = settings.admin_password
    
    if db.query(User).filter(User.username == username).first():
        print(f"Admin user with username '{username}' already exists.")
        return
        
    if db.query(User).filter(User.email == email).first():
        print(f"Admin user with email '{email}' already exists.")
        return

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
    """Main function to run the installation process."""
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
