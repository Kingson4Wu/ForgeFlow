#!/bin/bash
# 自动配置仓库 hooksPath（当前仓库 + 静默模式）

set -e

# 1. 配置 Git 使用仓库 hooks 目录
git config core.hooksPath hooks

# 2. 检查当前仓库是否启用 commit.gpgsign
GPG_SIGN=$(git config commit.gpgsign || echo "")

if [ -z "$GPG_SIGN" ]; then
  git config commit.gpgsign true
fi

# 3. 检查用户是否有 GPG key
GPG_KEY=$(git config user.signingkey || echo "")

if [ -z "$GPG_KEY" ]; then
  echo ""
  echo "⚠️  No GPG key configured for Git."
  echo "Generate one with:"
  echo "  gpg --full-generate-key"
  echo "Then set it with:"
  echo "  git config --global user.signingkey <KEY_ID>"
fi

# 4. 确保所有 hooks 都是可执行的
chmod +x hooks/*

