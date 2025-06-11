#!/bin/bash

# 快速重建前端腳本
# 使用方式: ./rebuild.sh

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  快速重建前端...${NC}"

# 進入前端目錄並構建
cd frontend
npm run build

# 複製構建結果到正確位置
cd ..
if [ -f "app/static/public/index.html" ]; then
    cp app/static/public/index.html app/static/index.html
    echo -e "${GREEN}✅ 已更新 index.html${NC}"
else
    echo -e "${RED}❌ 找不到構建好的 index.html${NC}"
fi

echo -e "${GREEN}✅ 前端重建完成！${NC}"
echo -e "${YELLOW}💡 請重新加載瀏覽器頁面查看更新${NC}" 