#!/bin/bash
# 快速提交并推送脚本
# 用法：./scripts/commit-push.sh "提交信息"

set -e

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "用法：$0 \"提交信息\""
    exit 1
fi

echo "📝 提交变更：$1"
git add -A
git commit -m "$1"
git push patdelphi main

echo "✅ 同步完成！"
