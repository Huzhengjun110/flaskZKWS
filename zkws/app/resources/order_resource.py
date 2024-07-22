from flask import Blueprint
from flask_restful import Api, Resource
from app.resources.schemas.order import order_parser, payment_parser
from app.services.order_service import createOrder, createPayment, checkPayment, getOrderList
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('orders', __name__, url_prefix='/orders')
api = Api(bp)


class Orders(Resource):

    def get(self):
        # 获取所有订单信息
        pass

    @jwt_required()
    def post(self):
        # 用户生成订单
        user_id = get_jwt_identity()
        data = order_parser.parse_args()
        return createOrder(user_id, data['product_id'], data['quantity'])


class UserOrders(Resource):
    @jwt_required()
    def get(self, user_id):
        # 根据用户id获取订单
        identity_user = get_jwt_identity()
        if identity_user == user_id:
            return getOrderList(user_id)
        else:
            return {
                       'msg': '账户异常'
                   }, 400

    @jwt_required()
    def delete(self, user_id):
        # 删除订单
        pass

    @jwt_required()
    def put(self, user_id):
        # 修改订单
        pass


class Payments(Resource):

    def get(self):
        # 获取所有支付订单信息
        pass

    @jwt_required()
    def post(self):
        # 用户生成支付订单
        data = payment_parser.parse_args()
        return createPayment(
            subject=data['subject'],
            order_number=data['order_number'],
            payment_method=data['payment_method'],
            return_url=data['return_url']
        )


class UserPayment(Resource):
    def get(self, order_number):
        return checkPayment(order_number)


api.add_resource(Orders, '/order')
api.add_resource(UserOrders, '/order/<int:user_id>')

api.add_resource(Payments, '/payment')
api.add_resource(UserPayment, '/payment/<string:order_number>')
