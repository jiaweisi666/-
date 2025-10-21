#!/bin/bash
# 使用 Gunicorn 启动应用
# --workers 4 表示启动4个工作进程来处理请求，增加并发能力
# --bind 0.0.0.0:${PORT:-5000} 是关键部分:
# - 0.0.0.0 表示监听所有网络接口，允许外部访问
# - ${PORT:-5000} 表示优先使用环境变量 $PORT (由云平台提供)，如果不存在，则默认使用 5000 端口
# app:app 指的是启动 app.py 文件中的 app 实例
gunicorn --workers 4 --bind 0.0.0.0:${PORT:-5000} app:app
