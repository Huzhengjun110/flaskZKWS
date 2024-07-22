from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.resources import user_resource, article_resource, order_resource, products_resource, ai_model_api, admin_resource


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    # 注册蓝图
    app.register_blueprint(user_resource.bp)
    app.register_blueprint(article_resource.bp)
    app.register_blueprint(order_resource.bp)
    app.register_blueprint(products_resource.bp)
    app.register_blueprint(ai_model_api.bp)
    app.register_blueprint(admin_resource.bp)
    return app
