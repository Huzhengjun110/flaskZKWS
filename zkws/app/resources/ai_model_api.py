from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Api, Resource
import requests

from app.extensions import db
from app.resources.schemas.ai_model import model_data
from app.models.user_model import UserCountsModel

bp = Blueprint('ai', __name__, url_prefix='/ai')
api = Api(bp)
AI_URL = 'http://172.20.19.121:8090/'


def checkCheckCounts(user_id, product_id):
    count = UserCountsModel.query.filter_by(user_id=user_id, product_id=product_id).first()
    if count.counts == 0:
        return None
    else:
        return count


# 公文写作
class AiWriteArticle(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 1  # ai写作的id为1
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkemiaobi_Gongwen', data={"send_text": data['send_text'], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# 公文扩写
class ExpandArticle(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 2  # ai扩写的id为2
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkemiaobi_Gongwen',
                                 data={"send_text": data['send_text'], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# 公文续写
class ContinueArticle(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 3  # ai续写的id为3
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkemiaobi_Gongwen',
                                 data={"send_text": data['send_text'], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# 公文润色
class PolishArticle(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 4  # ai写作的id为4
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkemiaobi_Gongwen',
                                 data={"send_text": data['send_text'], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# Kenlm模型审校
class AiCheckKenlm(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 5  # ai审校的id为5
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkeshenjiao_kenlm',
                                 data={"send_text": data["send_text"], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# MacBert模型审校
class AiCheckMacBert(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 5  # ai审校的id为5
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkeshenjiao_MacBert',
                                 data={"send_text": data["send_text"], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# T5模型审校
class AiCheckT5(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 5  # ai审校的id为5
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkeshenjiao_T5',
                                 data={"send_text": data["send_text"], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# GPT模型审校
class AiCheckGPT(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 5  # ai审校的id为5
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkeshenjiao_GPT',
                                 data={"send_text": data["send_text"], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()
        return our_str


# 聊天模型
class AiTalk(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        product_id = 6  # ai聊天的id为6
        count = checkCheckCounts(current_user_id, product_id)
        if count is None:
            return {
                "msg": "您的余额不足"
            }, 401
        count.counts -= 1
        data = model_data.parse_args()
        response = requests.post(AI_URL + 'zhongkemiaobi_Chat',
                                 data={"send_text": data["send_text"], "sender_name": data["sender_name"]})
        our_str = response.json()
        db.session.commit()

        return our_str


api.add_resource(AiTalk, '/talk')
api.add_resource(AiCheckKenlm, '/kenlm')
api.add_resource(AiCheckMacBert, '/MacBert')
api.add_resource(AiCheckT5, '/T5')
api.add_resource(AiCheckGPT, '/GPT')

api.add_resource(AiWriteArticle, '/write')
api.add_resource(ExpandArticle, '/expand')
api.add_resource(ContinueArticle, '/continue')
api.add_resource(PolishArticle, '/polish')
