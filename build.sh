#!/bin/bash

# VERSION
VERSION=$(date +%Y%m%d%H%M%S)

# 创建并使用一个新的 Buildx 构建器实例，如果已存在则使用现有的
BUILDER_NAME=multi-platform-build
docker buildx create --name $BUILDER_NAME --use || true
docker buildx use $BUILDER_NAME
docker buildx inspect --bootstrap

# 登录到 Docker Hub
docker login -u=your_user_name -p="your_access_token"

# 使用 Docker Buildx 构建镜像，同时标记为 latest 和 VERSION，支持多架构
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg NPM_CONFIG_REGISTRY=https://registry.npmmirror.com \
  -t your_user_name/pandora-plus-helper:$VERSION \
  -t your_user_name/pandora-plus-helper . \
  --push \
  --progress=plain

# 登出 Docker Hub
docker logout