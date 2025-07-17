#!/bin/bash
# 產生以當下時間為檔名的 git diff 結果 txt 檔案

date_str=$(date '+%Y%m%d_%H%M%S')
outfile="diff_$date_str.txt"
git diff > "$outfile"
echo "已產生 $outfile" 