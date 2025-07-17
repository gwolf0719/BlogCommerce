#!/usr/bin/env python3
"""
測試商品 Markdown 功能
"""
import sys
import os
sys.path.append('.')

from app.services.markdown_service import MarkdownService

def test_markdown():
    markdown_service = MarkdownService()
    
    test_content = """
# 商品特色

這是一個**優質商品**，具有以下特點：

## 主要功能
- 高品質材料
- 精緻工藝
- 耐用設計

### 使用說明
1. 開箱檢查
2. 按照說明書操作
3. 定期保養

> **注意事項**：請仔細閱讀使用說明

```python
# 範例代碼
print("Hello World")
```

更多資訊請參考 [官方網站](https://example.com)
"""
    
    html_result = markdown_service.render(test_content)
    print("Markdown 渲染結果：")
    print(html_result)
    print("\n測試完成！")

if __name__ == "__main__":
    test_markdown()