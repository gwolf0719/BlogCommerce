#!/usr/bin/env python3
"""
修正OpenAPI配置中的externalDocs問題
"""

import re

def fix_openapi_config():
    # 讀取main.py文件
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除所有的externalDocs區塊
    # 使用正則表達式匹配並移除
    pattern = r',\s*"externalDocs":\s*{\s*"description":\s*"[^"]*",\s*"url":\s*"[^"]*"\s*}'
    content = re.sub(pattern, '', content)
    
    # 寫回文件
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已移除所有externalDocs配置")
    print("✅ OpenAPI配置修正完成")

if __name__ == "__main__":
    fix_openapi_config() 