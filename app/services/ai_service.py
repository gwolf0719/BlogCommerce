import asyncio
import aiohttp
import json
import uuid
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models.settings import SystemSettings
from app.database import get_db

class AIService:
    """AI生成服務"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_available_models(self, provider: str, api_url: str, api_key: str) -> List[str]:
        """根據提供商取得可用模型列表"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {}
        endpoint = api_url.rstrip('/') + '/models'

        if provider in ['openai', 'custom']:
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
        elif provider == 'anthropic':
            if api_key:
                headers['x-api-key'] = api_key
            headers['anthropic-version'] = '2023-06-01'
        else:
            raise ValueError('不支援的AI提供商')

        async with self.session.get(endpoint, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise ValueError(f'取得模型列表失敗: {resp.status} {text}')
            data = await resp.json()

        if provider in ['openai', 'custom']:
            return [m.get('id') for m in data.get('data', [])]
        else:  # anthropic
            return [m.get('name') for m in data.get('models', [])]
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """獲取AI相關設定"""
        db = next(get_db())
        try:
            settings = {}
            ai_settings = db.query(SystemSettings).filter(
                SystemSettings.category == 'ai'
            ).all()
            
            for setting in ai_settings:
                settings[setting.key] = setting.parse_value()
            
            return settings
        finally:
            db.close()
    
    def is_ai_enabled(self) -> bool:
        """檢查AI功能是否啟用"""
        settings = self.get_ai_settings()
        return settings.get('ai_enabled', False)
    
    def is_image_generation_enabled(self) -> bool:
        """檢查圖片生成是否啟用"""
        settings = self.get_ai_settings()
        return settings.get('ai_image_enabled', False) and self.is_ai_enabled()
    
    async def generate_article(self, user_prompt: str, title_hint: str = None) -> Dict[str, Any]:
        """生成文章內容"""
        if not self.is_ai_enabled():
            raise ValueError("AI功能未啟用")
        
        settings = self.get_ai_settings()
        api_key = settings.get('ai_api_key')
        api_url = settings.get('ai_api_url', 'https://api.openai.com/v1')
        model = settings.get('ai_text_model', 'gpt-3.5-turbo')
        global_prompt = settings.get('ai_global_prompt', '')
        max_tokens = settings.get('ai_max_tokens', 2000)
        temperature = settings.get('ai_temperature', 0.7)
        
        if not api_key:
            raise ValueError("AI API金鑰未設定")
        
        # 構建提示詞
        system_prompt = f"""{global_prompt}

請根據以下要求生成一篇部落格文章，並以JSON格式返回：

{{
    "title": "文章標題",
    "subtitle": "文章副標題（可選）", 
    "excerpt": "文章摘要（150字以內）",
    "content": "文章內容（Markdown格式）",
    "tags": ["標籤1", "標籤2", "標籤3"],
    "meta_description": "SEO描述（160字以內）",
    "image_prompt": "用於生成特色圖片的英文提示詞"
}}

用戶需求: {user_prompt}
{f'標題提示: {title_hint}' if title_hint else ''}

請確保：
1. 文章內容豐富且有價值
2. 使用Markdown格式（包含標題、段落、列表等）
3. 標籤相關且有用
4. 圖片提示詞應該是簡潔的英文描述
5. 所有內容使用繁體中文
"""
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': temperature,
            'response_format': {'type': 'json_object'}
        }
        
        try:
            async with self.session.post(
                f'{api_url}/chat/completions',
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"API請求失敗: {response.status} - {error_text}")
                
                result = await response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析JSON回應
                try:
                    article_data = json.loads(content)
                    return article_data
                except json.JSONDecodeError as e:
                    raise ValueError(f"無法解析AI回應的JSON格式: {e}")
                    
        except aiohttp.ClientError as e:
            raise ValueError(f"網路請求錯誤: {e}")
    
    async def generate_image(self, prompt: str, style: str = "natural") -> str:
        """生成圖片"""
        if not self.is_image_generation_enabled():
            raise ValueError("圖片生成功能未啟用")
        
        settings = self.get_ai_settings()
        api_key = settings.get('ai_api_key')
        api_url = settings.get('ai_api_url', 'https://api.openai.com/v1')
        model = settings.get('ai_image_model', 'dall-e-3')
        
        if not api_key:
            raise ValueError("AI API金鑰未設定")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 增強提示詞
        enhanced_prompt = f"{prompt}, high quality, detailed, professional, {style} style"
        
        payload = {
            'model': model,
            'prompt': enhanced_prompt,
            'n': 1,
            'size': '1024x1024',
            'quality': 'standard',
            'response_format': 'url'
        }
        
        try:
            async with self.session.post(
                f'{api_url}/images/generations',
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"圖片生成API請求失敗: {response.status} - {error_text}")
                
                result = await response.json()
                image_url = result['data'][0]['url']
                
                # 下載並保存圖片
                return await self.download_and_save_image(image_url)
                
        except aiohttp.ClientError as e:
            raise ValueError(f"圖片生成網路錯誤: {e}")
    
    async def download_and_save_image(self, image_url: str) -> str:
        """下載並保存AI生成的圖片"""
        try:
            async with self.session.get(image_url) as response:
                if response.status != 200:
                    raise ValueError(f"圖片下載失敗: {response.status}")
                
                # 生成唯一文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"ai_generated_{timestamp}_{unique_id}.jpg"
                
                # 確保目錄存在
                upload_dir = "app/static/images/blog"
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存圖片
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                
                # 返回相對路徑
                return f"/static/images/blog/{filename}"
                
        except Exception as e:
            raise ValueError(f"圖片保存失敗: {e}")
    
    async def generate_complete_article(self, user_prompt: str, title_hint: str = None, generate_image: bool = True) -> Dict[str, Any]:
        """生成完整文章（包含圖片）"""
        try:
            # 生成文章內容
            article_data = await self.generate_article(user_prompt, title_hint)
            
            # 如果啟用圖片生成且用戶要求
            if generate_image and self.is_image_generation_enabled():
                image_prompt = article_data.get('image_prompt', article_data.get('title', ''))
                if image_prompt:
                    try:
                        image_path = await self.generate_image(image_prompt)
                        article_data['featured_image'] = image_path
                    except Exception as e:
                        # 圖片生成失敗不影響文章生成
                        print(f"圖片生成失敗: {e}")
                        article_data['featured_image'] = None
            
            return {
                'success': True,
                'data': article_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# 全域AI服務實例
ai_service = AIService() 