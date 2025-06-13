"""
Markdown 處理服務
"""
import markdown
import re
from typing import Optional
from markdown.extensions import codehilite, tables, toc, fenced_code


class MarkdownService:
    """Markdown 處理服務"""
    
    def __init__(self):
        # 配置 Markdown 擴展
        self.extensions = [
            'markdown.extensions.extra',     # 額外語法支援
            'markdown.extensions.codehilite', # 程式碼高亮
            'markdown.extensions.tables',    # 表格支援
            'markdown.extensions.toc',       # 目錄生成
            'markdown.extensions.fenced_code', # 圍欄程式碼塊
            'markdown.extensions.attr_list', # 屬性列表
        ]
        
        self.extension_configs = {
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': False,  # 不使用 pygments，使用內建樣式
                'noclasses': True,
                'linenos': False,
            },
            'markdown.extensions.toc': {
                'permalink': True,
                'permalink_title': '永久連結',
                'baselevel': 1,  # 改為從 H1 開始
                'toc_depth': 6,
            }
        }
    
    def render(self, content: str) -> str:
        """
        將 Markdown 內容轉換為 HTML
        
        Args:
            content: Markdown 內容
            
        Returns:
            HTML 內容
        """
        if not content:
            return ""
        
        try:
            md = markdown.Markdown(
                extensions=self.extensions,
                extension_configs=self.extension_configs
            )
            
            html = md.convert(content)
            
            # 後處理 HTML
            html = self._post_process_html(html)
            
            return html
            
        except Exception as e:
            # 如果 Markdown 處理失敗，返回原始內容
            print(f"Markdown 處理錯誤: {e}")
            return content.replace('\n', '<br>')
    
    def _post_process_html(self, html: str) -> str:
        """
        後處理 HTML 內容
        
        Args:
            html: 原始 HTML
            
        Returns:
            處理後的 HTML
        """
        # 為圖片添加響應式 CSS 類
        html = re.sub(
            r'<img([^>]*)>',
            r'<img\1 class="img-responsive">',
            html
        )
        
        # 為表格添加響應式包裝
        html = re.sub(
            r'<table([^>]*)>',
            r'<div class="table-responsive"><table\1 class="table table-bordered">',
            html
        )
        html = re.sub(
            r'</table>',
            r'</table></div>',
            html
        )
        
        # 為連結添加目標屬性（外部連結）
        html = re.sub(
            r'<a href="(https?://[^"]*)"([^>]*)>',
            r'<a href="\1"\2 target="_blank" rel="noopener noreferrer">',
            html
        )
        
        return html
    
    def extract_excerpt(self, content: str, max_length: int = 200) -> str:
        """
        從 Markdown 內容中提取摘要
        
        Args:
            content: Markdown 內容
            max_length: 最大長度
            
        Returns:
            摘要文字
        """
        if not content:
            return ""
        
        try:
            # 移除 Markdown 語法
            text = self._strip_markdown(content)
            
            # 清理空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 截取指定長度
            if len(text) > max_length:
                text = text[:max_length].rsplit(' ', 1)[0] + '...'
            
            return text
            
        except Exception as e:
            print(f"摘要提取錯誤: {e}")
            return content[:max_length] + '...' if len(content) > max_length else content
    
    def _strip_markdown(self, content: str) -> str:
        """
        移除 Markdown 語法，只保留純文字
        
        Args:
            content: Markdown 內容
            
        Returns:
            純文字內容
        """
        # 移除 Markdown 語法
        patterns = [
            r'!\[.*?\]\(.*?\)',           # 圖片
            r'\[([^\]]+)\]\([^\)]+\)',    # 連結
            r'`([^`]+)`',                 # 行內程式碼
            r'```[\s\S]*?```',            # 程式碼塊
            r'^#{1,6}\s*',                # 標題
            r'^\s*[-*+]\s+',              # 無序列表
            r'^\s*\d+\.\s+',              # 有序列表
            r'^\s*>\s*',                  # 引用
            r'\*\*([^*]+)\*\*',           # 粗體
            r'\*([^*]+)\*',               # 斜體
            r'~~([^~]+)~~',               # 刪除線
        ]
        
        text = content
        for pattern in patterns:
            if pattern.startswith('^'):
                # 多行模式
                text = re.sub(pattern, '', text, flags=re.MULTILINE)
            else:
                text = re.sub(pattern, r'\1', text)
        
        return text
    
    def get_toc(self, content: str) -> Optional[str]:
        """
        生成目錄
        
        Args:
            content: Markdown 內容
            
        Returns:
            目錄 HTML
        """
        if not content:
            return None
        
        try:
            md = markdown.Markdown(
                extensions=['markdown.extensions.toc'],
                extension_configs={
                    'markdown.extensions.toc': {
                        'permalink': True,
                        'permalink_title': '永久連結',
                        'baselevel': 2,
                    }
                }
            )
            
            md.convert(content)
            
            if hasattr(md, 'toc') and md.toc:
                return md.toc
            
            return None
            
        except Exception as e:
            print(f"目錄生成錯誤: {e}")
            return None


# 創建全局實例
markdown_service = MarkdownService() 