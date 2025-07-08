#!/bin/bash
npx vite build --watch &
VITE_PID=$!

# 檢查是否有 fswatch
if command -v fswatch &> /dev/null; then
    # 使用 fswatch 監聽目錄變化
    fswatch -o ../app/static/public/ | while read f; do
        if [ -f "../app/static/public/index.html" ]; then
            cp ../app/static/public/index.html ../app/static/index.html
            echo "$(date '+%H:%M:%S') ✅ 已自動更新 index.html (fswatch)"
        fi
    done &
    WATCH_PID=$!
else
    # 沒有 fswatch，使用定期檢查方式
    while true; do
        sleep 3
        if [ -f "../app/static/public/index.html" ]; then
            # 檢查文件是否有變化（比較修改時間）
            if [ "../app/static/public/index.html" -nt "../app/static/index.html" ]; then
                cp ../app/static/public/index.html ../app/static/index.html
                echo "$(date '+%H:%M:%S') ✅ 已自動更新 index.html (polling)"
            fi
        fi
    done &
    WATCH_PID=$!
fi

# 捕捉信號並清理
trap 'kill $VITE_PID $WATCH_PID 2>/dev/null; exit' SIGTERM SIGINT

wait $VITE_PID
