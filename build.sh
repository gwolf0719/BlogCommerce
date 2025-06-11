#!/bin/bash

echo "🚀 開始建置 BlogCommerce 管理後台..."

# 檢查 node_modules 是否存在
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安裝前端依賴..."
    cd frontend
    npm install
    cd ..
fi

# 建置前端
echo "🔧 建置 Vue 專案..."
cd frontend
npm run build
cd ..

# 修正路徑
echo "🔧 修正靜態檔案路徑..."
if [ -f "app/static/index.html" ]; then
    # 使用 sed 替換路徑（macOS 兼容）
    sed -i '' 's|href="/assets/|href="/static/assets/|g' app/static/index.html
    sed -i '' 's|src="/assets/|src="/static/assets/|g' app/static/index.html
    sed -i '' 's|href="/vite.svg"|href="/static/vite.svg"|g' app/static/index.html
fi

echo "✅ 建置完成！"
echo "🌐 您現在可以訪問 http://127.0.0.1:8001/admin/login"
echo ""
echo "💡 提示："
echo "   - 開發模式: cd frontend && npm run dev"
echo "   - 重新建置: ./build.sh"
echo "   - 監視建置: cd frontend && npm run build:watch" 