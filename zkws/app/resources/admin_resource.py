from flask import Blueprint
from flask_restful import Api, Resource
from app.services.admin_service import CreateAdminAccountService, AdminLoginService, UpdateAdminInformationService
from app.resources.schemas.admin_schema import adminData
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('admin', __name__, url_prefix='/admin')
api = Api(bp)


class AdminLogin(Resource):
    @jwt_required()
    def get(self):
        pass

    def post(self):
        data = adminData()
        return AdminLoginService(data.username, data.password)

    @jwt_required()
    def put(self):
        pass


class SuperAdmin(Resource):
    def get(self):
        # 获取全部管理员信息
        pass

    @jwt_required()
    def post(self):
        # 添加管理员
        current_account_id = get_jwt_identity()
        data = adminData()
        return CreateAdminAccountService(current_account_id, data.username, data.password, data.admin_type)

    @jwt_required()
    def put(self):
        # 修改管理员信息
        current_account_id = get_jwt_identity()
        data = adminData()
        return UpdateAdminInformationService(current_account_id, data.id, data.username, data.password, data.admin_type)

    @jwt_required()
    def delete(self):
        # 删除管理员
        data = adminData()
        return data


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


api.add_resource(AdminLogin, '/account')
api.add_resource(SuperAdmin, '/super')
