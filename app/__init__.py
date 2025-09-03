from flask import Flask, send_from_directory
from flask_cors import CORS
from .config import Config
from .database import db, init_db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 启用CORS
    CORS(app)

    # 初始化数据库
    init_db(app)

    # 设置路由
    from .routes import setup_routes
    setup_routes(app)

    # 添加前端静态文件服务
    @app.route('/')
    def serve_frontend():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('../frontend', path)

    return app