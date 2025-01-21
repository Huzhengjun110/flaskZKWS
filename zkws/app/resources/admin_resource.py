from functools import wraps

from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restful import Api, Resource, reqparse
from app.resources.schemas.admin_schema import adminData
from app.services.admin_service import *

bp = Blueprint('admin', __name__, url_prefix='/admin')
api = Api(bp)

# 定义角色和权限的映射
ROLES_PERMISSIONS = {
    'super_admin': ['super_admin', 'admin', 'normal'],
    'admin': ['admin', 'normal'],
    'normal': ['normal']
}


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            jwt_payload = get_jwt()
            claims = jwt_payload.get('role')
            if claims and permission in ROLES_PERMISSIONS[claims]:
                return function(*args, **kwargs)
            else:
                abort(403)

        return decorated_function

    return decorator


class AdminLogin(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return getAdminAccountById(user_id)

    def post(self):
        # 管理员登录
        data = adminData()
        return AdminLoginService(data.username, data.password)

    def put(self):
        # 管理员登录后可以修改用户名和密码
        data = adminData()
        return


class Admins(Resource):
    def get(self, admin_id):
        # 根据id查看管理员信息
        return getAdminAccountById(admin_id)

    def put(self, admin_id):
        # 修改管理员信息
        # 超级管理能修改所有管理员的信息(包括用户role)
        data = adminData()
        return UpdateAdminInformationService(admin_id, data.username, data.password, data.user_type)

    def delete(self, admin_id):
        # 删除管理员

        return


class AdminList(Resource):
    def get(self):
        # 返回管理员列表（可通过query过滤）
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=10, type=int)
        admin_name = request.args.get('admin_name', type=str)
        return getAdminAccountList(page, page_size, admin_name)

    def post(self):
        # 超级管理员能添加普通管理员
        data = adminData()
        return CreateAdminAccountService(data.username, data.password, data.type_id)


class Users(Resource):
    def get(self, user_id):
        pass

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class UsersList(Resource):
    def get(self):
        pass

    def post(self):
        pass


class ProductInfo(Resource):
    def get(self):
        # 获取商品信息
        pass

    def post(self):
        # 添加商品信息
        pass

    def put(self):
        # 修改商品信息
        pass

    def delete(self):
        # 删除商品信息
        pass


class OrderInfo(Resource):
    def get(self):
        # 获取订单信息
        pass

    def post(self):
        # 添加订单信息
        pass

    def put(self):
        # 修改订单信息
        pass


class Articles(Resource):
    # 用户公文管理
    def get(self, article_id):
        pass


class ArticlesList(Resource):
    # 用户公文管理
    def get(self):
        pass


class ExampleArticlesResource(Resource):
    # 处理单个范文请求
    # 使用@jwt_required()进行登录验证，且要对该用户进行鉴权
    @permission_required('admin')
    def get(self, article_id):
        # 根据id获取范文
        return getArticleById(article_id)

    @permission_required('admin')
    def put(self, article_id):
        # 根据id修改范文
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        article_data = parser.parse_args()
        return updateArticleById(article_id, article_data.title, article_data.type, article_data.content)

    @permission_required('admin')
    def delete(self, article_id):
        # 根据id删除范文
        return deleteArticleById(article_id)


class ExampleArticlesListResource(Resource):
    # 处理范文列表的请求
    @permission_required('admin')
    def get(self):
        # 返回范文列表（可通过query过滤）
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=10, type=int)
        article_type = request.args.get('article_type', type=str)
        article_title = request.args.get('article_title', type=str)
        return getArticlesList(article_type, article_title, page, page_size)

    @permission_required('admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        article_data = parser.parse_args()
        return insertArticleIntoDatabase(article_title=article_data.title, article_type=article_data.type,
                                         article_content=article_data.content)


api.add_resource(AdminLogin, '/login')
api.add_resource(Admins, '/admins/<int:admin_id>')
api.add_resource(AdminList, '/admins')

api.add_resource(Users, '/users/<int:user_id>')
api.add_resource(UsersList, '/users')

api.add_resource(Articles, '/articles/<int:artice_id>')
api.add_resource(ArticlesList, '/articles')

api.add_resource(ExampleArticlesListResource, '/example')
api.add_resource(ExampleArticlesResource, '/example/<int:article_id>')
