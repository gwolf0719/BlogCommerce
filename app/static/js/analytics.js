// 流量統計系統
class Analytics {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.startTime = Date.now();
        this.lastActivity = Date.now();
        this.pageViews = 0;
        this.currentPage = {
            url: window.location.href,
            title: document.title,
            type: this.getPageType(),
            contentId: this.getContentId()
        };
        
        // 初始化
        this.init();
    }
    
    init() {
        // 記錄頁面瀏覽
        this.trackPageView();
        
        // 監聽頁面離開事件
        window.addEventListener('beforeunload', () => {
            this.trackPageLeave();
        });
        
        // 監聽頁面可見性變化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.trackPageLeave();
            } else {
                this.updateActivity();
            }
        });
        
        // 定時更新活動狀態
        setInterval(() => {
            this.updateActivity();
        }, 30000); // 每30秒
        
        // 監聽滾動和點擊事件
        let scrollDepth = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            scrollDepth = Math.max(scrollDepth, currentScroll);
            this.updateActivity();
        });
        
        document.addEventListener('click', (e) => {
            this.trackClick(e);
            this.updateActivity();
        });
    }
    
    getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('analytics_session_id');
        if (!sessionId) {
            sessionId = this.generateUUID();
            sessionStorage.setItem('analytics_session_id', sessionId);
        }
        return sessionId;
    }
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    getPageType() {
        const path = window.location.pathname;
        
        if (path === '/') return 'home';
        if (path.startsWith('/blog/') && path !== '/blog') return 'blog';
        if (path === '/blog') return 'blog_list';
        if (path.startsWith('/product/')) return 'product';
        if (path === '/products') return 'product_list';
        if (path === '/cart') return 'cart';
        if (path === '/checkout') return 'checkout';
        if (path.startsWith('/admin')) return 'admin';
        
        return 'other';
    }
    
    getContentId() {
        const path = window.location.pathname;
        const match = path.match(/\/(blog|product)\/(.+)/);
        
        if (match) {
            // 從 DOM 中獲取內容 ID（如果可用）
            const contentElement = document.querySelector('[data-content-id]');
            if (contentElement) {
                return parseInt(contentElement.getAttribute('data-content-id'));
            }
        }
        
        return null;
    }
    
    async trackPageView() {
        try {
            const data = {
                page_url: this.currentPage.url,
                page_type: this.currentPage.type,
                content_id: this.currentPage.contentId,
                page_title: this.currentPage.title,
                session_id: this.sessionId
            };
            
            await fetch('/api/analytics/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            this.pageViews++;
            
        } catch (error) {
            console.warn('Analytics tracking failed:', error);
        }
    }
    
    trackPageLeave() {
        const viewDuration = Math.round((Date.now() - this.startTime) / 1000);
        
        // 使用 sendBeacon 確保數據能發送
        const data = {
            page_url: this.currentPage.url,
            page_type: this.currentPage.type,
            content_id: this.currentPage.contentId,
            view_duration: viewDuration,
            session_id: this.sessionId
        };
        
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/analytics/track', JSON.stringify(data));
        }
    }
    
    trackClick(event) {
        const element = event.target;
        const clickData = {
            element_type: element.tagName.toLowerCase(),
            element_class: element.className,
            element_id: element.id,
            element_text: element.textContent?.substring(0, 100),
            page_url: this.currentPage.url,
            x: event.clientX,
            y: event.clientY
        };
        
        // 特殊處理重要點擊
        if (element.tagName === 'A') {
            clickData.link_url = element.href;
        } else if (element.tagName === 'BUTTON' || element.type === 'submit') {
            clickData.action = 'button_click';
        }
        
        this.sendEvent('click', clickData);
    }
    
    updateActivity() {
        this.lastActivity = Date.now();
        
        // 定期發送心跳
        if (this.lastActivity - this.startTime > 30000) { // 30秒後開始發送心跳
            this.sendHeartbeat();
        }
    }
    
    async sendHeartbeat() {
        try {
            await fetch('/api/analytics/heartbeat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    page_url: this.currentPage.url,
                    active_time: Date.now() - this.startTime
                })
            });
        } catch (error) {
            // 靜默失敗
        }
    }
    
    async sendEvent(eventType, eventData) {
        try {
            await fetch('/api/analytics/event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: eventType,
                    event_data: eventData,
                    session_id: this.sessionId,
                    page_url: this.currentPage.url,
                    timestamp: Date.now()
                })
            });
        } catch (error) {
            console.warn('Event tracking failed:', error);
        }
    }
    
    // 自定義事件追蹤方法
    track(eventName, properties = {}) {
        this.sendEvent('custom', {
            event_name: eventName,
            properties: properties
        });
    }
    
    // 電商相關事件
    trackAddToCart(productId, productName, price, quantity = 1) {
        this.sendEvent('add_to_cart', {
            product_id: productId,
            product_name: productName,
            price: price,
            quantity: quantity
        });
    }
    
    trackPurchase(orderId, total, items) {
        this.sendEvent('purchase', {
            order_id: orderId,
            total: total,
            items: items
        });
    }
    
    trackSearch(query, results = null) {
        this.sendEvent('search', {
            query: query,
            results_count: results
        });
    }
    
    // 內容相關事件
    trackShare(contentType, contentId, platform) {
        this.sendEvent('share', {
            content_type: contentType,
            content_id: contentId,
            platform: platform
        });
    }
    
    trackDownload(fileUrl, fileName) {
        this.sendEvent('download', {
            file_url: fileUrl,
            file_name: fileName
        });
    }
    
    trackVideoPlay(videoId, videoTitle) {
        this.sendEvent('video_play', {
            video_id: videoId,
            video_title: videoTitle
        });
    }
    
    trackFormSubmission(formName, formData = {}) {
        this.sendEvent('form_submit', {
            form_name: formName,
            form_data: formData
        });
    }
}

// 自動初始化
if (typeof window !== 'undefined') {
    window.analytics = new Analytics();
    
    // 提供全局追蹤函數
    window.trackEvent = function(eventName, properties) {
        window.analytics.track(eventName, properties);
    };
    
    window.trackAddToCart = function(productId, productName, price, quantity) {
        window.analytics.trackAddToCart(productId, productName, price, quantity);
    };
    
    window.trackPurchase = function(orderId, total, items) {
        window.analytics.trackPurchase(orderId, total, items);
    };
    
    window.trackSearch = function(query, results) {
        window.analytics.trackSearch(query, results);
    };
    
    window.trackShare = function(contentType, contentId, platform) {
        window.analytics.trackShare(contentType, contentId, platform);
    };
} 