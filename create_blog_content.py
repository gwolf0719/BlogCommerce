#!/usr/bin/env python3
"""
生成豐富的部落格內容腳本
"""

import sys
sys.path.append('.')

from app.database import get_db
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from datetime import datetime, timedelta
import random

# 部落格分類數據
BLOG_CATEGORIES = [
    {
        "name": "科技趨勢",
        "slug": "tech-trends",
        "description": "探索最新的科技發展和未來趨勢",
        "type": "blog"
    },
    {
        "name": "生活風格",
        "slug": "lifestyle",
        "description": "分享日常生活中的美好時光和生活技巧",
        "type": "blog"
    },
    {
        "name": "旅遊攻略",
        "slug": "travel",
        "description": "世界各地的旅遊景點和實用攻略",
        "type": "blog"
    },
    {
        "name": "美食分享",
        "slug": "food",
        "description": "美味料理食譜和餐廳推薦",
        "type": "blog"
    },
    {
        "name": "健康養生",
        "slug": "health",
        "description": "健康生活方式和養生知識分享",
        "type": "blog"
    },
    {
        "name": "職場成長",
        "slug": "career",
        "description": "職業發展和個人成長的經驗分享",
        "type": "blog"
    }
]

# 部落格標籤
BLOG_TAGS = [
    {"name": "人工智慧", "slug": "ai", "type": "blog"},
    {"name": "機器學習", "slug": "machine-learning", "type": "blog"},
    {"name": "區塊鏈", "slug": "blockchain", "type": "blog"},
    {"name": "物聯網", "slug": "iot", "type": "blog"},
    {"name": "雲端運算", "slug": "cloud-computing", "type": "blog"},
    {"name": "穿搭", "slug": "fashion", "type": "blog"},
    {"name": "居家佈置", "slug": "home-decor", "type": "blog"},
    {"name": "運動健身", "slug": "fitness", "type": "blog"},
    {"name": "閱讀", "slug": "reading", "type": "blog"},
    {"name": "攝影", "slug": "photography", "type": "blog"},
    {"name": "日本", "slug": "japan", "type": "blog"},
    {"name": "歐洲", "slug": "europe", "type": "blog"},
    {"name": "東南亞", "slug": "southeast-asia", "type": "blog"},
    {"name": "背包客", "slug": "backpacking", "type": "blog"},
    {"name": "美食", "slug": "gourmet", "type": "blog"},
    {"name": "甜點", "slug": "dessert", "type": "blog"},
    {"name": "咖啡", "slug": "coffee", "type": "blog"},
    {"name": "料理", "slug": "cooking", "type": "blog"},
    {"name": "瑜伽", "slug": "yoga", "type": "blog"},
    {"name": "冥想", "slug": "meditation", "type": "blog"},
    {"name": "營養", "slug": "nutrition", "type": "blog"},
    {"name": "職涯", "slug": "career-development", "type": "blog"},
    {"name": "創業", "slug": "startup", "type": "blog"},
    {"name": "投資理財", "slug": "investment", "type": "blog"}
]

# 豐富的部落格文章內容
BLOG_POSTS = [
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
        "tags": ["人工智慧", "機器學習", "科技趨勢"]
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
        
        <blockquote>
        "擁有的越少，自由就越多。" - 梭羅
        </blockquote>
        
        <p>極簡生活是一個持續的過程，重要的是找到適合自己的平衡點。</p>
        """,
        "categories": ["生活風格"],
        "tags": ["極簡主義", "生活方式", "心靈成長"]
    },
    {
        "title": "日本櫻花季完整攻略：最佳賞櫻地點與時間",
        "slug": "japan-cherry-blossom-guide",
        "excerpt": "完整的日本櫻花季旅遊指南，包含最佳賞櫻景點、花期預測和實用旅行貼士",
        "content": """
        <h2>日本櫻花季概況</h2>
        <p>日本的櫻花季是世界上最美麗的自然景觀之一。每年3-5月，從南到北，櫻花依序綻放，為整個日本島嶼穿上粉色的外衣。</p>
        
        <h3>櫻花前線時間表</h3>
        <table>
        <tr><th>地區</th><th>花期</th><th>最佳觀賞時間</th></tr>
        <tr><td>沖繩</td><td>1-2月</td><td>1月下旬-2月上旬</td></tr>
        <tr><td>九州</td><td>3月下旬-4月上旬</td><td>3月底-4月初</td></tr>
        <tr><td>關西</td><td>3月底-4月中旬</td><td>4月上旬</td></tr>
        <tr><td>關東</td><td>3月底-4月中旬</td><td>4月上旬</td></tr>
        <tr><td>東北</td><td>4月中旬-5月上旬</td><td>4月下旬</td></tr>
        <tr><td>北海道</td><td>4月下旬-5月中旬</td><td>5月上旬</td></tr>
        </table>
        
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
        "tags": ["日本", "櫻花", "旅遊", "攝影"]
    },
    {
        "title": "在家製作完美義式濃縮咖啡的秘訣",
        "slug": "perfect-espresso-at-home",
        "excerpt": "學習如何在家中製作媲美咖啡店品質的義式濃縮咖啡，從器具選擇到沖煮技巧的完整指南",
        "content": """
        <h2>義式濃縮咖啡的魅力</h2>
        <p>義式濃縮咖啡（Espresso）是咖啡世界的精髓，30毫升的液體中蘊含著豐富的香氣和層次。在家製作完美的espresso不僅省錢，更能享受沖煮的樂趣。</p>
        
        <h3>必備器具</h3>
        
        <h4>咖啡機選擇</h4>
        <ul>
        <li><strong>入門級</strong>：De'Longhi EC155 ($100-150)</li>
        <li><strong>中階</strong>：Breville Bambino Plus ($200-300)</li>
        <li><strong>專業級</strong>：Rancilio Silvia ($400-600)</li>
        </ul>
        
        <h4>磨豆機</h4>
        <ul>
        <li><strong>手動</strong>：1Zpresso JX-Pro</li>
        <li><strong>電動</strong>：Baratza Encore ESP</li>
        </ul>
        
        <h4>其他工具</h4>
        <ul>
        <li>電子秤（精確到0.1g）</li>
        <li>分粉器（Distributor）</li>
        <li>填壓器（Tamper）</li>
        <li>計時器</li>
        </ul>
        
        <h3>完美Espresso的參數</h3>
        <table>
        <tr><th>參數</th><th>數值</th></tr>
        <tr><td>咖啡粉用量</td><td>18-20g</td></tr>
        <tr><td>萃取液體量</td><td>36-40ml</td></tr>
        <tr><td>萃取時間</td><td>25-30秒</td></tr>
        <tr><td>水溫</td><td>90-96°C</td></tr>
        <tr><td>壓力</td><td>9 bar</td></tr>
        </table>
        
        <h3>沖煮步驟</h3>
        
        <h4>1. 準備工作</h4>
        <ol>
        <li>預熱機器和杯子</li>
        <li>磨製新鮮咖啡豆（細研磨）</li>
        <li>秤量18g咖啡粉</li>
        </ol>
        
        <h4>2. 裝粉與填壓</h4>
        <ol>
        <li>將咖啡粉平均分布在濾杯中</li>
        <li>用分粉器整平粉層</li>
        <li>用30磅力量垂直填壓</li>
        </ol>
        
        <h4>3. 萃取</h4>
        <ol>
        <li>鎖上濾杯到機器</li>
        <li>立即開始萃取</li>
        <li>觀察咖啡液流出的顏色和速度</li>
        <li>25-30秒後停止萃取</li>
        </ol>
        
        <h3>品質判斷標準</h3>
        
        <h4>視覺</h4>
        <ul>
        <li>顏色：深褐色帶有焦糖色澤</li>
        <li>油脂：表面有豐富的金黃色crema</li>
        <li>流速：開始像蜂蜜一樣緩慢流出</li>
        </ul>
        
        <h4>味覺</h4>
        <ul>
        <li>平衡：酸甜苦三味平衡</li>
        <li>口感：濃郁但不過度苦澀</li>
        <li>餘韻：持久的香氣和甜感</li>
        </ul>
        
        <h3>常見問題解決</h3>
        
        <table>
        <tr><th>問題</th><th>可能原因</th><th>解決方法</th></tr>
        <tr><td>萃取過快</td><td>研磨太粗</td><td>調細研磨度</td></tr>
        <tr><td>萃取過慢</td><td>研磨太細</td><td>調粗研磨度</td></tr>
        <tr><td>味道酸澀</td><td>萃取不足</td><td>增加萃取時間或調細研磨</td></tr>
        <tr><td>味道苦澀</td><td>過度萃取</td><td>減少萃取時間或調粗研磨</td></tr>
        </table>
        
        <blockquote>
        "好的espresso應該像交響樂一樣，有開場、高潮和完美的結尾。" - 義大利咖啡大師
        </blockquote>
        
        <p>製作完美的espresso需要練習和耐心。每一杯都是一次學習的機會，享受這個過程本身就是最大的樂趣。</p>
        """,
        "categories": ["美食分享"],
        "tags": ["咖啡", "料理", "生活技巧"]
    },
    {
        "title": "瑜伽初學者完整指南：從基礎體式到建立日常練習",
        "slug": "yoga-beginner-complete-guide",
        "excerpt": "為瑜伽初學者提供全面的入門指南，包括基礎體式、呼吸技巧和如何建立持續的練習習慣",
        "content": """
        <h2>瑜伽的益處</h2>
        <p>瑜伽不僅是一種運動，更是一種生活方式。它結合了身體的伸展、力量訓練、呼吸練習和冥想，為身心帶來全面的健康益處。</p>
        
        <h3>身體益處</h3>
        <ul>
        <li><strong>增強柔韌性</strong>：改善關節活動度</li>
        <li><strong>提升力量</strong>：特別是核心和平衡力</li>
        <li><strong>改善姿勢</strong>：減少因久坐造成的問題</li>
        <li><strong>促進血液循環</strong>：增強心血管健康</li>
        <li><strong>減輕疼痛</strong>：特別是背痛和關節痛</li>
        </ul>
        
        <h3>心理益處</h3>
        <ul>
        <li><strong>減輕壓力</strong>：降低皮質醇水平</li>
        <li><strong>改善睡眠</strong>：幫助放鬆和入睡</li>
        <li><strong>提升專注力</strong>：訓練正念和集中注意力</li>
        <li><strong>增強自信</strong>：透過挑戰自己建立信心</li>
        <li><strong>情緒調節</strong>：學習觀察和管理情緒</li>
        </ul>
        
        <h3>準備開始</h3>
        
        <h4>必備用品</h4>
        <ul>
        <li><strong>瑜伽墊</strong>：提供穩定和緩衝（建議6mm厚度）</li>
        <li><strong>瑜伽磚</strong>：協助完成困難體式</li>
        <li><strong>瑜伽帶</strong>：增加伸展幅度</li>
        <li><strong>舒適服裝</strong>：彈性好、透氣的運動服</li>
        </ul>
        
        <h4>練習環境</h4>
        <ul>
        <li>安靜、通風的空間</li>
        <li>溫度適中（20-25°C）</li>
        <li>足夠的活動空間</li>
        <li>柔和的光線</li>
        </ul>
        
        <h3>基礎體式（Asanas）</h3>
        
        <h4>1. 山式（Tadasana）</h4>
        <p><strong>功效：</strong>改善姿勢，培養身體意識</p>
        <p><strong>步驟：</strong></p>
        <ol>
        <li>雙腳併攏站立，腳趾張開</li>
        <li>腿部肌肉啟動，膝蓋骨向上提</li>
        <li>脊椎拉長，肩膀放鬆</li>
        <li>雙手自然垂放身側</li>
        <li>深呼吸，保持1-2分鐘</li>
        </ol>
        
        <h4>2. 下犬式（Adho Mukha Svanasana）</h4>
        <p><strong>功效：</strong>全身伸展，增強手臂和肩膀力量</p>
        <p><strong>步驟：</strong></p>
        <ol>
        <li>從四足跪姿開始</li>
        <li>腳趾下壓，抬起臀部</li>
        <li>雙手推地，形成倒V字型</li>
        <li>努力讓腳跟著地</li>
        <li>保持5-8個呼吸</li>
        </ol>
        
        <h4>3. 戰士一式（Virabhadrasana I）</h4>
        <p><strong>功效：</strong>增強腿部力量，開展胸部</p>
        <p><strong>步驟：</strong></p>
        <ol>
        <li>從山式開始，左腳向後跨一大步</li>
        <li>前腳膝蓋彎曲90度</li>
        <li>後腳45度角踩地</li>
        <li>雙手向上舉起</li>
        <li>保持5-8個呼吸，換邊重複</li>
        </ol>
        
        <h4>4. 樹式（Vrksasana）</h4>
        <p><strong>功效：</strong>提升平衡感，強化站立腿</p>
        <p><strong>步驟：</strong></p>
        <ol>
        <li>單腳站立，另一腳腳底貼大腿內側</li>
        <li>膝蓋朝外打開</li>
        <li>雙手合十於胸前或舉過頭頂</li>
        <li>凝視固定點保持平衡</li>
        <li>保持30秒-1分鐘，換邊</li>
        </ol>
        
        <h4>5. 嬰兒式（Balasana）</h4>
        <p><strong>功效：</strong>放鬆休息，緩解壓力</p>
        <p><strong>步驟：</strong></p>
        <ol>
        <li>跪坐，大腳趾相觸</li>
        <li>膝蓋分開與臀部同寬</li>
        <li>身體前傾，額頭觸地</li>
        <li>雙手向前伸展或放身側</li>
        <li>深呼吸，想停多久就停多久</li>
        </ol>
        
        <h3>呼吸技巧（Pranayama）</h3>
        
        <h4>腹式呼吸</h4>
        <ol>
        <li>舒適地坐著或躺下</li>
        <li>一手放胸部，一手放腹部</li>
        <li>緩慢深吸氣，讓腹部像氣球一樣擴張</li>
        <li>慢慢呼氣，腹部收縮</li>
        <li>重複10-15次</li>
        </ol>
        
        <h4>等長呼吸</h4>
        <ol>
        <li>吸氣數4拍</li>
        <li>屏氣4拍</li>
        <li>呼氣4拍</li>
        <li>屏氣4拍</li>
        <li>重複5-10個循環</li>
        </ol>
        
        <h3>建立日常練習</h3>
        
        <h4>初學者時間表</h4>
        <ul>
        <li><strong>第1-2週</strong>：每天10-15分鐘</li>
        <li><strong>第3-4週</strong>：每天20-30分鐘</li>
        <li><strong>第2個月</strong>：每天30-45分鐘</li>
        <li><strong>長期目標</strong>：每天45-60分鐘</li>
        </ul>
        
        <h4>練習貼士</h4>
        <ol>
        <li><strong>保持一致</strong>：每天同一時間練習</li>
        <li><strong>循序漸進</strong>：不要勉強做困難體式</li>
        <li><strong>聆聽身體</strong>：避免疼痛和不適</li>
        <li><strong>專注呼吸</strong>：將注意力保持在呼吸上</li>
        <li><strong>保持耐心</strong>：進步需要時間</li>
        </ol>
        
        <h3>常見錯誤與避免方法</h3>
        
        <table>
        <tr><th>錯誤</th><th>後果</th><th>正確做法</th></tr>
        <tr><td>急於求成</td><td>容易受傷</td><td>循序漸進，尊重身體限制</td></tr>
        <tr><td>比較心態</td><td>失去練習樂趣</td><td>專注自己的進步</td></tr>
        <tr><td>忽略呼吸</td><td>無法獲得最大益處</td><td>保持深長的呼吸</td></tr>
        <tr><td>不定期練習</td><td>難以看到進步</td><td>建立固定練習時間</td></tr>
        </table>
        
        <blockquote>
        "瑜伽不是要你變得完美，而是要你變得完整。" - 古印度智慧
        </blockquote>
        
        <p>記住，瑜伽是一個旅程，不是目的地。享受每一次練習，感受身心的變化，你會發現瑜伽帶給你的不僅是身體的健康，更是內心的平靜與智慧。</p>
        """,
        "categories": ["健康養生"],
        "tags": ["瑜伽", "運動健身", "冥想", "健康"]
    },
    {
        "title": "職場新人必知：如何在前三個月建立良好印象",
        "slug": "first-three-months-career-success",
        "excerpt": "給職場新人的實用建議，分享如何在入職前三個月展現專業能力並建立良好的人際關係",
        "content": """
        <h2>職場第一印象的重要性</h2>
        <p>俗話說「第一印象決定一切」，在職場上更是如此。前三個月是新員工的黃金期，也是建立專業形象、展現能力的關鍵時刻。</p>
        
        <h3>第一個月：適應與觀察</h3>
        
        <h4>1. 做好基本準備</h4>
        <ul>
        <li><strong>提早到達</strong>：提前15-30分鐘到辦公室</li>
        <li><strong>著裝得體</strong>：觀察公司文化，選擇合適的服裝風格</li>
        <li><strong>準備文具</strong>：筆記本、筆、名片夾等基本用品</li>
        <li><strong>整理工作區</strong>：保持桌面整潔有序</li>
        </ul>
        
        <h4>2. 積極學習公司文化</h4>
        <ul>
        <li>仔細閱讀員工手冊</li>
        <li>了解公司歷史和價值觀</li>
        <li>觀察同事間的互動模式</li>
        <li>學習公司的工作流程和制度</li>
        </ul>
        
        <h4>3. 建立人際關係</h4>
        <ul>
        <li><strong>主動自我介紹</strong>：向同事介紹自己</li>
        <li><strong>記住名字</strong>：努力記住同事的姓名和職位</li>
        <li><strong>參與社交活動</strong>：積極參加公司聚餐或活動</li>
        <li><strong>保持謙遜</strong>：以學習者的心態面對一切</li>
        </ul>
        
        <h3>第二個月：展現能力</h3>
        
        <h4>1. 主動承擔責任</h4>
        <ul>
        <li>完成分配的任務並超出期望</li>
        <li>主動詢問是否需要協助</li>
        <li>提出改善建議（謹慎且建設性）</li>
        <li>承認錯誤並積極改正</li>
        </ul>
        
        <h4>2. 提升專業技能</h4>
        <ul>
        <li><strong>持續學習</strong>：利用下班時間提升相關技能</li>
        <li><strong>請教同事</strong>：虛心向資深同事學習</li>
        <li><strong>參加培訓</strong>：積極參與公司提供的培訓課程</li>
        <li><strong>閱讀資料</strong>：研讀與工作相關的資料和文件</li>
        </ul>
        
        <h4>3. 有效溝通</h4>
        <ul>
        <li><strong>清晰表達</strong>：用簡潔明確的語言溝通</li>
        <li><strong>積極聆聽</strong>：認真聽取他人的意見和建議</li>
        <li><strong>及時回應</strong>：迅速回覆郵件和訊息</li>
        <li><strong>定期匯報</strong>：主動向主管報告工作進度</li>
        </ul>
        
        <h3>第三個月：鞏固地位</h3>
        
        <h4>1. 成為可信賴的團隊成員</h4>
        <ul>
        <li><strong>守時守信</strong>：準時完成承諾的工作</li>
        <li><strong>品質導向</strong>：確保工作品質符合標準</li>
        <li><strong>團隊合作</strong>：主動協助團隊達成目標</li>
        <li><strong>正面態度</strong>：保持樂觀積極的工作態度</li>
        </ul>
        
        <h4>2. 建立專業形象</h4>
        <ul>
        <li><strong>專業知識</strong>：在專業領域展現深度</li>
        <li><strong>解決問題</strong>：主動解決工作中遇到的問題</li>
        <li><strong>創新思維</strong>：提出創新的想法和解決方案</li>
        <li><strong>領導潛力</strong>：在小項目中展現領導能力</li>
        </ul>
        
        <h3>關鍵成功因素</h3>
        
        <h4>1. 時間管理</h4>
        <table>
        <tr><th>時間段</th><th>活動</th><th>重點</th></tr>
        <tr><td>9:00-10:00</td><td>計劃當日工作</td><td>優先級排序</td></tr>
        <tr><td>10:00-12:00</td><td>處理重要任務</td><td>專注度最高</td></tr>
        <tr><td>14:00-16:00</td><td>會議和溝通</td><td>協作時間</td></tr>
        <tr><td>16:00-18:00</td><td>完成瑣碎事務</td><td>整理總結</td></tr>
        </table>
        
        <h4>2. 情緒管理</h4>
        <ul>
        <li><strong>壓力調節</strong>：學會管理工作壓力</li>
        <li><strong>情緒控制</strong>：保持冷靜和專業</li>
        <li><strong>積極心態</strong>：將挑戰視為成長機會</li>
        <li><strong>工作生活平衡</strong>：維持健康的作息</li>
        </ul>
        
        <h3>避免的常見錯誤</h3>
        
        <h4>❌ 不要做的事情</h4>
        <ul>
        <li>過度表現或搶風頭</li>
        <li>批評公司或同事</li>
        <li>拒絕學習新技能</li>
        <li>忽視公司政策和規定</li>
        <li>在社交媒體上發布不當內容</li>
        <li>過度分享個人生活</li>
        <li>與同事產生衝突</li>
        </ul>
        
        <h4>✅ 應該做的事情</h4>
        <ul>
        <li>保持學習者的謙虛態度</li>
        <li>主動尋求回饋和建議</li>
        <li>建立良好的工作習慣</li>
        <li>投資於人際關係建立</li>
        <li>展現對公司的忠誠和承諾</li>
        <li>持續改善工作表現</li>
        <li>保持專業和正面的形象</li>
        </ul>
        
        <h3>建立長期職涯發展</h3>
        
        <h4>1. 設定目標</h4>
        <ul>
        <li><strong>短期目標</strong>：3-6個月內要達成的里程碑</li>
        <li><strong>中期目標</strong>：1-2年的職位晉升計劃</li>
        <li><strong>長期目標</strong>：5-10年的職涯願景</li>
        </ul>
        
        <h4>2. 建立人脈</h4>
        <ul>
        <li>參加行業活動和研討會</li>
        <li>加入專業協會或組織</li>
        <li>在LinkedIn上建立專業檔案</li>
        <li>尋找導師或職涯教練</li>
        </ul>
        
        <h4>3. 持續學習</h4>
        <ul>
        <li>關注行業趨勢和發展</li>
        <li>參加線上課程和研習</li>
        <li>閱讀專業書籍和期刊</li>
        <li>學習新的軟體和技術</li>
        </ul>
        
        <blockquote>
        "成功不是一個目的地，而是一個旅程。每一天都是學習和成長的機會。" - 職場智慧
        </blockquote>
        
        <h3>結語</h3>
        <p>職場成功不是一蹴而就的，需要持續的努力和智慧。在前三個月建立的良好基礎，將成為未來職涯發展的重要資產。記住，每個人的職涯路徑都不同，重要的是找到適合自己的節奏，持續學習和成長。</p>
        
        <p>保持開放的心態，勇於面對挑戰，相信自己的能力，你一定能在職場上建立成功的職業生涯。</p>
        """,
        "categories": ["職場成長"],
        "tags": ["職涯", "職場技巧", "人際關係", "專業發展"]
    }
]

def create_blog_content():
    """創建豐富的部落格分類、標籤和文章內容"""
    
    # 獲取資料庫連接
    db = next(get_db())
    
    try:
        print("開始創建部落格內容...")
        
        # 1. 創建分類
        print("創建部落格分類...")
        categories_map = {}
        for cat_data in BLOG_CATEGORIES:
            # 檢查是否已存在
            existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing:
                category = Category(**cat_data)
                db.add(category)
                db.flush()
                categories_map[cat_data["name"]] = category
                print(f"  ✓ 創建分類: {cat_data['name']}")
            else:
                categories_map[cat_data["name"]] = existing
                print(f"  - 分類已存在: {cat_data['name']}")
        
        # 2. 創建標籤
        print("創建部落格標籤...")
        tags_map = {}
        for tag_data in BLOG_TAGS:
            # 檢查是否已存在
            existing = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
            if not existing:
                tag = Tag(**tag_data)
                db.add(tag)
                db.flush()
                tags_map[tag_data["name"]] = tag
                print(f"  ✓ 創建標籤: {tag_data['name']}")
            else:
                tags_map[tag_data["name"]] = existing
                print(f"  - 標籤已存在: {tag_data['name']}")
        
        # 3. 創建文章
        print("創建部落格文章...")
        for i, post_data in enumerate(BLOG_POSTS):
            # 檢查是否已存在
            existing = db.query(Post).filter(Post.slug == post_data["slug"]).first()
            if not existing:
                # 創建文章
                post = Post(
                    title=post_data["title"],
                    slug=post_data["slug"],
                    excerpt=post_data["excerpt"],
                    content=post_data["content"],
                    is_published=True,
                    created_at=datetime.now() - timedelta(days=len(BLOG_POSTS)-i)
                )
                
                # 添加分類
                for cat_name in post_data["categories"]:
                    if cat_name in categories_map:
                        post.categories.append(categories_map[cat_name])
                
                # 添加標籤
                for tag_name in post_data["tags"]:
                    if tag_name in tags_map:
                        post.tags.append(tags_map[tag_name])
                
                db.add(post)
                print(f"  ✓ 創建文章: {post_data['title']}")
            else:
                print(f"  - 文章已存在: {post_data['title']}")
        
        # 提交所有變更
        db.commit()
        print("\n🎉 部落格內容創建完成！")
        print(f"總共創建了 {len(BLOG_CATEGORIES)} 個分類、{len(BLOG_TAGS)} 個標籤和 {len(BLOG_POSTS)} 篇文章")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 創建過程中發生錯誤: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_blog_content() 