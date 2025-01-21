from flask import Blueprint
from flask_restful import Api, Resource
from app.models.order import ProductsModel

bp = Blueprint('products', __name__, url_prefix='/products')
api = Api(bp)


class Products(Resource):
    def get(self):
        # 返回所有的商品
        return ProductsModel.return_all()


api.add_resource(Products, '/product')
