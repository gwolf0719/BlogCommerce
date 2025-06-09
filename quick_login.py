#!/usr/bin/env python3
"""
快速登入管理後台腳本
"""

import webbrowser
import time

def quick_login():
    """快速登入指導"""
    print("🚀 BlogCommerce 快速登入")
    print("=" * 40)
    print()
    print("📋 登入資訊:")
    print("   👤 用戶名: admin")
    print("   🔑 密碼: admin123")
    print()
    print("🔗 正在打開登入頁面...")
    
    # 打開登入頁面
    webbrowser.open('http://127.0.0.1:8000/admin/login')
    
    print("✅ 登入頁面已打開")
    print()
    print("📝 請在瀏覽器中:")
    print("   1. 輸入用戶名: admin")
    print("   2. 輸入密碼: admin123") 
    print("   3. 點擊登入按鈕")
    print()
    print("🎯 登入成功後，您可以訪問:")
    print("   ⚙️ 系統設定: http://127.0.0.1:8000/admin/settings")
    print("   📊 儀表板: http://127.0.0.1:8000/admin")
    print("   📦 訂單管理: http://127.0.0.1:8000/admin/orders")
    print()
    
    # 等待用戶登入
    input("按 Enter 鍵繼續（當您完成登入後）...")
    
    print("🔗 正在打開系統設定頁面...")
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:8000/admin/settings')
    print("✅ 系統設定頁面已打開")
    print()
    print("🎉 如果您已成功登入，現在應該可以看到系統設定頁面了！")

if __name__ == "__main__":
    quick_login() 