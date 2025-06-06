#!/usr/bin/env python3
"""
生成豐富的部落格內容腳本 - 2024版本
包含各種主題的高品質中文文章
"""

import sys
sys.path.append('.')

from app.database import get_db
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from app.models.user import User
from datetime import datetime, timedelta
import random

def create_comprehensive_blog_content():
    """創建綜合性的部落格內容"""
    
    print("🚀 開始創建部落格內容...")
    
    # 獲取數據庫連接
    db = next(get_db())
    
    # 創建或獲取管理員用戶
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@blogcommerce.com",
            password_hash="hashed_password_placeholder",
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ 創建管理員用戶")
    
    # 部落格分類
    blog_categories = [
        {
            "name": "科技趨勢",
            "slug": "tech-trends", 
            "description": "探索最新的科技發展和未來趨勢",
            "type": "BLOG"
        },
        {
            "name": "生活風格",
            "slug": "lifestyle",
            "description": "分享日常生活中的美好時光和生活技巧", 
            "type": "BLOG"
        },
        {
            "name": "旅遊攻略",
            "slug": "travel",
            "description": "世界各地的旅遊景點和實用攻略",
            "type": "BLOG"
        },
        {
            "name": "美食分享", 
            "slug": "food",
            "description": "美味料理食譜和餐廳推薦",
            "type": "BLOG"
        },
        {
            "name": "健康養生",
            "slug": "health",
            "description": "健康生活方式和養生知識分享",
            "type": "BLOG"
        },
        {
            "name": "職場成長",
            "slug": "career", 
            "description": "職業發展和個人成長的經驗分享",
            "type": "BLOG"
        }
    ]
    
    # 部落格標籤
    blog_tags = [
        {"name": "人工智慧", "slug": "ai", "type": "BLOG"},
        {"name": "機器學習", "slug": "machine-learning", "type": "BLOG"},
        {"name": "穿搭", "slug": "fashion", "type": "BLOG"},
        {"name": "居家佈置", "slug": "home-decor", "type": "BLOG"},
        {"name": "運動健身", "slug": "fitness", "type": "BLOG"},
        {"name": "攝影", "slug": "photography", "type": "BLOG"},
        {"name": "日本", "slug": "japan", "type": "BLOG"},
        {"name": "歐洲", "slug": "europe", "type": "BLOG"},
        {"name": "背包客", "slug": "backpacking", "type": "BLOG"},
        {"name": "美食", "slug": "gourmet", "type": "BLOG"},
        {"name": "咖啡", "slug": "coffee", "type": "BLOG"},
        {"name": "料理", "slug": "cooking", "type": "BLOG"},
        {"name": "瑜伽", "slug": "yoga", "type": "BLOG"},
        {"name": "冥想", "slug": "meditation", "type": "BLOG"},
        {"name": "職涯", "slug": "career-development", "type": "BLOG"},
        {"name": "創業", "slug": "startup", "type": "BLOG"}
    ]
    
    # 創建分類
    category_objects = {}
    for cat_data in blog_categories:
        existing_cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing_cat:
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                type=cat_data["type"]
            )
            db.add(category)
            category_objects[cat_data["name"]] = category
        else:
            category_objects[cat_data["name"]] = existing_cat
    
    db.commit()
    print("✅ 創建部落格分類")
    
    # 創建標籤
    tag_objects = {}
    for tag_data in blog_tags:
        existing_tag = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
        if not existing_tag:
            tag = Tag(
                name=tag_data["name"],
                slug=tag_data["slug"],
                type=tag_data["type"]
            )
            db.add(tag)
            tag_objects[tag_data["name"]] = tag
        else:
            tag_objects[tag_data["name"]] = existing_tag
    
    db.commit()
    print("✅ 創建部落格標籤")
    
    # 豐富的部落格文章內容
    blog_posts = [
        {
            "title": "2024年人工智慧發展趨勢：從ChatGPT到多模態AI",
            "slug": "ai-trends-2024-chatgpt-multimodal",
            "excerpt": "探索2024年AI技術的最新發展，包括大型語言模型、多模態AI和AGI的進展",
            "content": """
<h2>人工智慧的快速發展</h2>
<p>2024年是人工智慧技術突飛猛進的一年。從ChatGPT的爆紅到各種AI工具的普及，我們正見證著一個全新時代的到來。</p>

<h3>大型語言模型的演進</h3>
<p>GPT-4、Claude、Gemini等大型語言模型不斷突破，在理解能力、推理能力和創造能力方面都有顯著提升。這些模型不僅能處理文字，還能理解圖像、音頻等多種媒體格式。</p>

<h3>多模態AI的興起</h3>
<p>多模態AI技術讓機器能夠同時處理文字、圖像、聲音等不同類型的資訊，為AI應用開啟了更多可能性。</p>

<h3>AI在各行業的應用</h3>
<ul>
<li>醫療：AI輔助診斷和藥物研發</li>
<li>教育：個人化學習助手</li>
<li>金融：智能投資顧問</li>
<li>製造：自動化生產優化</li>
</ul>

<p>未來，AI將更深入地融入我們的日常生活，改變我們工作和生活的方式。</p>
            """,
            "categories": ["科技趨勢"],
            "tags": ["人工智慧", "機器學習"]
        },
        {
            "title": "極簡生活：如何在繁忙世界中找到內心平靜",
            "slug": "minimalist-living-inner-peace",
            "excerpt": "分享極簡生活的理念和實踐方法，幫助你在物質豐富的時代找到真正的幸福",
            "content": """
<h2>什麼是極簡生活？</h2>
<p>極簡生活不僅僅是減少物品，更是一種生活哲學。它追求的是用更少的物質獲得更多的自由和幸福。</p>

<h3>極簡生活的核心原則</h3>
<ol>
<li><strong>有意識的選擇</strong>：每一個決定都要深思熟慮</li>
<li><strong>質量優於數量</strong>：選擇真正需要和喜愛的物品</li>
<li><strong>體驗重於物質</strong>：投資在經歷而非物品上</li>
<li><strong>時間的珍貴</strong>：把時間花在真正重要的事情上</li>
</ol>

<h3>如何開始極簡生活</h3>
<h4>1. 整理空間</h4>
<p>從衣櫃開始，保留真正喜歡和經常穿的衣服。接著整理書籍、文件和其他個人物品。</p>

<h4>2. 數位極簡</h4>
<p>清理手機APP、社交媒體帳號，減少數位干擾，專注於真正重要的連結。</p>

<h4>3. 時間管理</h4>
<p>學會說不，專注於能帶來價值和意義的活動。</p>

<blockquote>"擁有的越少，自由就越多。" - 梭羅</blockquote>

<p>極簡生活是一個持續的過程，重要的是找到適合自己的平衡點。</p>
            """,
            "categories": ["生活風格"],
            "tags": ["穿搭", "居家佈置"]
        },
        {
            "title": "日本櫻花季完整攻略：最佳賞櫻地點與時間",
            "slug": "japan-cherry-blossom-guide",
            "excerpt": "完整的日本櫻花季旅遊指南，包含最佳賞櫻景點、花期預測和實用旅行貼士",
            "content": """
<h2>日本櫻花季概況</h2>
<p>日本的櫻花季是世界上最美麗的自然景觀之一。每年3-5月，從南到北，櫻花依序綻放，為整個日本島嶼穿上粉色的外衣。</p>

<h3>必訪賞櫻景點</h3>

<h4>東京地區</h4>
<ul>
<li><strong>上野公園</strong>：東京最知名的賞櫻地點，有1000多株櫻花樹</li>
<li><strong>新宿御苑</strong>：各種櫻花品種，花期較長</li>
<li><strong>千鳥淵</strong>：夜櫻燈光秀特別美麗</li>
<li><strong>目黑川</strong>：河岸兩旁的櫻花隧道</li>
</ul>

<h4>京都地區</h4>
<ul>
<li><strong>清水寺</strong>：古寺配櫻花的經典組合</li>
<li><strong>哲學之道</strong>：2公里的櫻花小徑</li>
<li><strong>嵐山</strong>：山櫻與竹林的美景</li>
<li><strong>圓山公園</strong>：京都最受歡迎的賞櫻地點</li>
</ul>

<h3>賞櫻小貼士</h3>
<ol>
<li><strong>提前訂房</strong>：櫻花季是旅遊旺季，住宿需要提前預訂</li>
<li><strong>關注天氣</strong>：雨天和強風會影響花期</li>
<li><strong>早起行動</strong>：避開人潮，享受寧靜的賞櫻時光</li>
<li><strong>準備野餐</strong>：日本人喜歡在櫻花樹下野餐，這叫「花見」</li>
</ol>

<p>櫻花的美在於它的短暫，正如日本文化中的「物哀」美學，提醒我們珍惜當下的美好時光。</p>
            """,
            "categories": ["旅遊攻略"],
            "tags": ["日本", "攝影", "背包客"]
        },
        {
            "title": "在家製作完美義式濃縮咖啡的秘訣",
            "slug": "perfect-espresso-at-home",
            "excerpt": "學會在家製作專業級義式濃縮咖啡的技巧，從選豆到萃取的完整指南",
            "content": """
<h2>義式濃縮咖啡的基礎</h2>
<p>義式濃縮咖啡（Espresso）是所有咖啡飲品的基礎，掌握了製作技巧，就能在家享受咖啡館等級的美味。</p>

<h3>必備器材</h3>
<ul>
<li><strong>濃縮咖啡機</strong>：家用半自動或全自動咖啡機</li>
<li><strong>咖啡磨豆機</strong>：磨出均勻細緻的咖啡粉</li>
<li><strong>電子秤</strong>：精確控制咖啡粉和水的比例</li>
<li><strong>壓粉器</strong>：均勻壓實咖啡粉</li>
<li><strong>萃取杯</strong>：專業的濃縮咖啡杯</li>
</ul>

<h3>選擇咖啡豆</h3>
<p>好的咖啡豆是成功的一半：</p>
<ul>
<li><strong>新鮮度</strong>：選擇烘焙日期在2-4週內的咖啡豆</li>
<li><strong>烘焙度</strong>：中深烘焙最適合製作濃縮咖啡</li>
<li><strong>產地</strong>：巴西、哥倫比亞、衣索比亞都是不錯的選擇</li>
</ul>

<h3>製作步驟</h3>
<ol>
<li><strong>研磨咖啡豆</strong>：使用18-20克咖啡豆，磨成細粉</li>
<li><strong>填粉</strong>：將咖啡粉均勻放入把手中</li>
<li><strong>壓粉</strong>：用30磅的力道均勻壓實</li>
<li><strong>萃取</strong>：25-30秒萃取出30-35ml的濃縮咖啡</li>
<li><strong>觀察</strong>：咖啡液應該呈現金黃色澤，有豐富的Crema</li>
</ol>

<h3>常見問題解決</h3>
<table class="table">
<thead>
<tr><th>問題</th><th>可能原因</th><th>解決方法</th></tr>
</thead>
<tbody>
<tr><td>萃取過快</td><td>研磨太粗</td><td>調細研磨度</td></tr>
<tr><td>萃取過慢</td><td>研磨太細</td><td>調粗研磨度</td></tr>
<tr><td>味道太酸</td><td>萃取不足</td><td>延長萃取時間</td></tr>
<tr><td>味道太苦</td><td>萃取過度</td><td>縮短萃取時間</td></tr>
</tbody>
</table>

<p>製作完美的濃縮咖啡需要不斷練習和調整，每一次的嘗試都是向完美邁進的一步。</p>
            """,
            "categories": ["美食分享"],
            "tags": ["咖啡", "料理", "美食"]
        },
        {
            "title": "瑜伽初學者指南：開始你的身心靈健康之旅",
            "slug": "yoga-beginner-guide",
            "excerpt": "瑜伽入門完整指南，包含基礎動作、呼吸技巧和練習建議",
            "content": """
<h2>瑜伽的起源與哲學</h2>
<p>瑜伽起源於古印度，是一門結合身體、心靈和精神的綜合性練習。「瑜伽」一詞源自梵文「Yoga」，意為「結合」或「連接」。</p>

<h3>瑜伽的益處</h3>
<h4>身體層面</h4>
<ul>
<li>增強柔軟度和肌力</li>
<li>改善姿勢和平衡感</li>
<li>促進血液循環</li>
<li>緩解慢性疼痛</li>
</ul>

<h4>心理層面</h4>
<ul>
<li>減輕壓力和焦慮</li>
<li>提升專注力</li>
<li>改善睡眠品質</li>
<li>增強自信心</li>
</ul>

<h3>適合初學者的瑜伽動作</h3>

<h4>1. 山式（Tadasana）</h4>
<p>最基本的站立姿勢，學會正確的身體對齊。</p>
<p><strong>步驟</strong>：雙腳併攏站立，重心均勻分布，脊椎挺直，雙手自然垂放身側。</p>

<h4>2. 下犬式（Downward-Facing Dog）</h4>
<p>全身性的伸展動作，強化手臂和腿部肌肉。</p>
<p><strong>步驟</strong>：四足跪姿開始，雙手撐地，臀部向上推，形成倒V字形。</p>

<h4>3. 嬰兒式（Child's Pose）</h4>
<p>放鬆和休息的姿勢，可以隨時使用。</p>
<p><strong>步驟</strong>：跪坐，額頭貼地，雙臂向前伸展或放在身側。</p>

<h4>4. 戰士一式（Warrior I）</h4>
<p>強化腿部和核心的平衡動作。</p>
<p><strong>步驟</strong>：弓箭步站立，前腿彎曲，後腿伸直，雙手向上舉起。</p>

<h3>呼吸技巧</h3>
<p>瑜伽中的呼吸（Pranayama）是連接身心的橋樑：</p>
<ul>
<li><strong>腹式呼吸</strong>：深沉的腹部呼吸，放鬆神經系統</li>
<li><strong>三段式呼吸</strong>：胸腹協調的完整呼吸</li>
<li><strong>交替鼻孔呼吸</strong>：平衡左右腦的呼吸法</li>
</ul>

<h3>建立練習習慣</h3>
<ol>
<li><strong>從短時間開始</strong>：每天15-20分鐘即可</li>
<li><strong>選擇固定時間</strong>：晨間或睡前都是不錯的選擇</li>
<li><strong>創造舒適環境</strong>：安靜、通風的空間</li>
<li><strong>聆聽身體</strong>：不強迫，尊重身體的限制</li>
</ol>

<blockquote>"瑜伽不是要你變得完美，而是要你變得完整。"</blockquote>

<p>瑜伽是一個終身的學習過程，重要的不是動作的完美，而是在練習中找到身心的平衡與和諧。</p>
            """,
            "categories": ["健康養生"],
            "tags": ["瑜伽", "運動健身", "冥想"]
        },
        {
            "title": "遠程工作時代：如何打造高效的居家辦公環境",
            "slug": "remote-work-home-office-setup",
            "excerpt": "分享打造理想居家辦公空間的實用建議，提升工作效率和生活品質",
            "content": """
<h2>遠程工作的新常態</h2>
<p>隨著科技發展和疫情影響，遠程工作已成為許多人的日常。一個良好的居家辦公環境不僅能提升工作效率，還能改善工作與生活的平衡。</p>

<h3>硬體設備配置</h3>

<h4>電腦設備</h4>
<ul>
<li><strong>高效能電腦</strong>：確保足夠的處理能力和記憶體</li>
<li><strong>雙螢幕設置</strong>：提升多工處理效率</li>
<li><strong>人體工學鍵盤滑鼠</strong>：減少長期使用的疲勞</li>
<li><strong>高品質網路攝影機</strong>：確保視訊會議品質</li>
</ul>

<h4>辦公家具</h4>
<ul>
<li><strong>人體工學椅子</strong>：支撐腰部，可調節高度</li>
<li><strong>升降桌</strong>：可坐可站的彈性工作方式</li>
<li><strong>螢幕支架</strong>：調整到適當的視線高度</li>
<li><strong>充足收納</strong>：保持工作空間整潔</li>
</ul>

<h3>環境優化</h3>

<h4>照明設計</h4>
<ul>
<li><strong>自然光線</strong>：儘量靠近窗戶，但避免直射螢幕</li>
<li><strong>檯燈補光</strong>：提供均勻的工作照明</li>
<li><strong>環境燈光</strong>：營造舒適的氛圍</li>
</ul>

<h4>聲音環境</h4>
<ul>
<li><strong>降噪耳機</strong>：專注工作時使用</li>
<li><strong>背景音樂</strong>：選擇有助集中的音樂</li>
<li><strong>隔音處理</strong>：減少外部干擾</li>
</ul>

<h3>工作習慣養成</h3>

<h4>時間管理</h4>
<ol>
<li><strong>固定作息</strong>：保持規律的工作時間</li>
<li><strong>番茄工作法</strong>：25分鐘專注工作，5分鐘休息</li>
<li><strong>時間區塊</strong>：為不同任務分配特定時段</li>
<li><strong>明確界線</strong>：區分工作時間和私人時間</li>
</ol>

<h4>健康管理</h4>
<ul>
<li><strong>定期休息</strong>：每小時站起來活動5分鐘</li>
<li><strong>眼部保健</strong>：遵循20-20-20法則</li>
<li><strong>運動習慣</strong>：每天至少30分鐘的身體活動</li>
<li><strong>健康飲食</strong>：準備營養均衡的工作餐點</li>
</ul>

<h3>數位工具推薦</h3>

<h4>協作工具</h4>
<ul>
<li><strong>Slack/Teams</strong>：團隊溝通平台</li>
<li><strong>Zoom/Google Meet</strong>：視訊會議軟體</li>
<li><strong>Notion/Trello</strong>：專案管理工具</li>
<li><strong>Google Workspace</strong>：雲端協作套件</li>
</ul>

<h4>生產力工具</h4>
<ul>
<li><strong>RescueTime</strong>：時間追蹤和分析</li>
<li><strong>Forest</strong>：專注力培養APP</li>
<li><strong>Todoist</strong>：任務管理工具</li>
<li><strong>Calendly</strong>：會議排程工具</li>
</ul>

<h3>心理健康維護</h3>

<h4>社交連結</h4>
<ul>
<li>定期與同事進行非正式聊天</li>
<li>參加線上團隊建設活動</li>
<li>維持與朋友家人的聯繫</li>
</ul>

<h4>壓力管理</h4>
<ul>
<li>練習深呼吸和冥想</li>
<li>設置明確的工作邊界</li>
<li>培養興趣愛好</li>
<li>尋求專業協助（如需要）</li>
</ul>

<h3>成本效益分析</h3>
<table class="table">
<thead>
<tr><th>項目</th><th>建議預算</th><th>效益</th></tr>
</thead>
<tbody>
<tr><td>人體工學椅</td><td>NT$15,000-30,000</td><td>減少腰背痛，提升舒適度</td></tr>
<tr><td>升降桌</td><td>NT$8,000-20,000</td><td>改善姿勢，增加活動</td></tr>
<tr><td>雙螢幕</td><td>NT$10,000-25,000</td><td>提升工作效率30%</td></tr>
<tr><td>降噪耳機</td><td>NT$5,000-15,000</td><td>提升專注力，減少干擾</td></tr>
</tbody>
</table>

<p>投資打造一個良好的居家辦公環境，不僅能提升工作效率，也是對自己健康和職業發展的長期投資。</p>
            """,
            "categories": ["職場成長"],
            "tags": ["職涯", "創業"]
        },
        {
            "title": "歐洲背包客攻略：30天走訪10個國家的預算與路線規劃",
            "slug": "europe-backpacking-30-days-guide",
            "excerpt": "詳細的歐洲背包客旅行指南，包含路線規劃、預算控制和實用貼士",
            "content": """
<h2>歐洲背包客旅行概述</h2>
<p>歐洲豐富的歷史文化、便利的交通網路和相對安全的環境，使其成為背包客的理想目的地。30天的歐洲之旅可以讓你深度體驗不同國家的魅力。</p>

<h3>推薦路線：經典環歐路線</h3>
<ol>
<li><strong>倫敦，英國</strong>（3天）- 起點：大英博物館、倫敦眼</li>
<li><strong>巴黎，法國</strong>（4天）- 浪漫之都：羅浮宮、艾菲爾鐵塔</li>
<li><strong>阿姆斯特丹，荷蘭</strong>（2天）- 自行車城市：運河、梵谷博物館</li>
<li><strong>柏林，德國</strong>（3天）- 歷史重鎮：柏林圍牆、布蘭登堡門</li>
<li><strong>布拉格，捷克</strong>（3天）- 童話城市：老城廣場、布拉格城堡</li>
<li><strong>維也納，奧地利</strong>（2天）- 音樂之都：美泉宮、聖史蒂芬大教堂</li>
<li><strong>威尼斯，義大利</strong>（2天）- 水上城市：聖馬可廣場、貢多拉</li>
<li><strong>佛羅倫斯，義大利</strong>（3天）- 文藝復興搖籃：烏菲茲美術館</li>
<li><strong>羅馬，義大利</strong>（3天）- 永恆之城：競技場、梵蒂岡</li>
<li><strong>巴塞隆納，西班牙</strong>（4天）- 高第建築：聖家堂、公園</li>
</ol>

<h3>預算規劃</h3>

<h4>每日預算分配（中等水準）</h4>
<ul>
<li><strong>住宿</strong>：€25-35（青年旅館共用房間）</li>
<li><strong>餐飲</strong>：€20-30（早餐自備、午餐簡單、晚餐餐廳）</li>
<li><strong>交通</strong>：€15-25（市內交通和城際移動平均）</li>
<li><strong>景點</strong>：€10-20（門票、導覽等）</li>
<li><strong>其他</strong>：€10-15（購物、零食、緊急費用）</li>
</ul>

<p><strong>每日總預算：€80-125</strong></p>
<p><strong>30天總預算：€2,400-3,750（約NT$84,000-131,000）</strong></p>

<h3>省錢小技巧</h3>

<h4>住宿省錢</h4>
<ol>
<li>選擇多人房而非雙人房</li>
<li>選擇市中心以外的住宿</li>
<li>提前預訂獲得早鳥優惠</li>
<li>考慮沙發衝浪（CouchSurfing）</li>
</ol>

<h4>餐飲省錢</h4>
<ol>
<li>選擇有廚房的住宿，自己烹飪</li>
<li>購買當地市場的食材</li>
<li>尋找當地人推薦的平價餐廳</li>
<li>利用Happy Hour時段用餐</li>
</ol>

<h3>安全注意事項</h3>
<ul>
<li>保持警覺，注意扒手</li>
<li>不要在公共場所展示貴重物品</li>
<li>告知家人朋友你的行程</li>
<li>購買旅行保險</li>
<li>備份重要文件</li>
</ul>

<blockquote>"旅行不是逃避生活，而是確保生活不會從你身邊逃走。"</blockquote>

<p>歐洲背包客旅行是一次難忘的人生體驗，不僅能開闊視野，還能培養獨立解決問題的能力。充分的準備和開放的心態是成功旅行的關鍵。</p>
            """,
            "categories": ["旅遊攻略"],
            "tags": ["歐洲", "背包客", "攝影"]
        }
    ]
    
    # 創建文章
    for i, post_data in enumerate(blog_posts):
        existing_post = db.query(Post).filter(Post.slug == post_data["slug"]).first()
        if existing_post:
            print(f"⚠️  文章已存在: {post_data['title']}")
            continue
            
        # 創建隨機的創建時間（過去30天內）
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        
        post = Post(
            title=post_data["title"],
            slug=post_data["slug"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            is_published=True,
            featured_image=f"/static/images/blog/blog-{i+1}.jpg",
            meta_title=post_data["title"],
            meta_description=post_data["excerpt"],
            created_at=created_at
        )
        
        # 添加分類
        for cat_name in post_data["categories"]:
            if cat_name in category_objects:
                post.categories.append(category_objects[cat_name])
        
        # 添加標籤
        for tag_name in post_data["tags"]:
            if tag_name in tag_objects:
                post.tags.append(tag_objects[tag_name])
        
        db.add(post)
        print(f"✅ 創建文章: {post.title}")
    
    try:
        db.commit()
        print("🎉 所有部落格內容創建完成！")
        print(f"📊 統計：")
        print(f"   - 分類數量：{len(blog_categories)}")
        print(f"   - 標籤數量：{len(blog_tags)}")
        print(f"   - 文章數量：{len(blog_posts)}")
        
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_comprehensive_blog_content() 