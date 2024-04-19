FROM node:16 as web-builder

WORKDIR /app
COPY ./frontend .
RUN npm install
RUN DISABLE_ESLINT_PLUGIN='true' npm run build


FROM python:3.9-slim-bookworm AS python-builder
WORKDIR /app
COPY . /app
RUN rm -rf /app/frontend/*
COPY --from=web-builder /app/dist ./frontend/dist
RUN pip install -r requirements.txt --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# 创建数据存储目录
RUN mkdir -p /data
EXPOSE 8182
# 数据库初始化/升级
RUN ["chmod", "+x", "/app/docker_start.sh"]
# 启动waitress
ENTRYPOINT ["/app/docker_start.sh"]