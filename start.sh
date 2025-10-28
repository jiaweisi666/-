#!/bin/bash

# 设置 Gunicorn 作为生产环境的 WSGI 服务器
# --workers 4: 使用4个工作进程来处理请求，提高并发能力
# --bind 0.0.0.0:${PORT:-5000}: 监听所有网络接口。端口由 Render 提供的 PORT 环境变量指定，如果未提供则默认为 5000
# app:app: 指定要运行的应用。第一个 'app' 指的是 app.py 文件，第二个 'app' 指的是该文件中的 Flask 实例 `app = Flask(__name__)`

gunicorn --workers 4 --bind 0.0.0.0:${PORT:-5000} app:app