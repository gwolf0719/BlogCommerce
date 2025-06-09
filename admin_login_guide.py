#!/usr/bin/env python3
"""
管理員登入指導工具
"""

import webbrowser
import time
import sys

def open_admin_login():
    """打開管理員登入頁面"""
    print("🔐 BlogCommerce 管理員登入指導")
    print("=" * 50)
    print()
    
    print("📋 登入資訊:")
    print("   🌐 登入網址: http://127.0.0.1:8000/admin/login")
    print("   👤 用戶名: admin")
    print("   🔑 密碼: admin123")
    print()
    
    print("📝 登入步驟:")
    print("   1. 即將自動打開登入頁面")
    print("   2. 輸入用戶名: admin")
    print("   3. 輸入密碼: admin123")
    print("   4. 點擊「登入」按鈕")
    print("   5. 成功後可訪問所有管理功能")
    print()
    
    print("🎯 主要管理頁面:")
    print("   📊 儀表板: http://127.0.0.1:8000/admin")
    print("   📝 文章管理: http://127.0.0.1:8000/admin/posts")
    print("   🛍️ 商品管理: http://127.0.0.1:8000/admin/products") 
    print("   📦 訂單管理: http://127.0.0.1:8000/admin/orders")
    print("   👥 會員管理: http://127.0.0.1:8000/admin/users")
    print("   ⚙️ 系統設定: http://127.0.0.1:8000/admin/settings")
    print("   📈 流量分析: http://127.0.0.1:8000/admin/analytics")
    print()
    
    # 詢問是否要打開瀏覽器
    response = input("是否要自動打開登入頁面？(Y/n): ").strip().lower()
    
    if response == '' or response == 'y' or response == 'yes':
        print("🚀 正在打開瀏覽器...")
        try:
            webbrowser.open('http://127.0.0.1:8000/admin/login')
            print("✅ 瀏覽器已打開，請按照上述資訊登入")
        except Exception as e:
            print(f"❌ 無法自動打開瀏覽器: {e}")
            print("📋 請手動打開瀏覽器並訪問: http://127.0.0.1:8000/admin/login")
    else:
        print("📋 請手動打開瀏覽器並訪問: http://127.0.0.1:8000/admin/login")
    
    print()
    print("💡 小提示:")
    print("   - 登入後會自動保存登入狀態")
    print("   - 如果忘記密碼，可運行 debug_login.py 重設")
    print("   - 遇到問題可查看終端的錯誤訊息")


def check_server_status():
    """檢查服務器狀態"""
    import requests
    
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✅ 服務器運行正常")
            return True
        else:
            print(f"⚠️ 服務器回應異常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器")
        print("💡 請先運行: python run.py")
        return False
    except Exception as e:
        print(f"❌ 檢查服務器時發生錯誤: {e}")
        return False


def main():
    """主函數"""
    print("🛡️ 檢查服務器狀態...")
    
    if not check_server_status():
        print("\n⚠️ 服務器未運行，請先啟動服務器:")
        print("   cd /Users/james/Project/BlogCommerce")
        print("   source venv/bin/activate")
        print("   python run.py")
        print("\n然後重新運行此腳本")
        return
    
    print()
    open_admin_login()


if __name__ == "__main__":
    main() 