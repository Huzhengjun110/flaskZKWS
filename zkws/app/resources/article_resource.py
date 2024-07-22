from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.article_service import returnAllExampleArticles, returnAllUserArticlesById, createUserArticle, updateUserArticle
from app.resources.schemas.article import new_article_data, update_articles_data

bp = Blueprint('article', __name__, url_prefix='/article')
api = Api(bp)


class ArticleUserList(Resource):

    @jwt_required()
    def post(self, user_id):
        # 用户新建公文
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return {
                       'msg': '用户状态异常！！！'
                   }, 400
        data = new_article_data.parse_args()
        article_type = data['type']
        title = data['title']
        content = data['content']
        return createUserArticle(user_id,article_type,title,content)

    @jwt_required()
    def put(self, user_id):
        # 用户修改公文
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return {
                'msg': '用户状态异常！！！'
            }, 400
        data = update_articles_data.parse_args()
        article_id = data['article_id']
        article_type = data['type']
        title = data['title']
        content = data['content']
        return updateUserArticle(article_id, article_type, title, content)

    @jwt_required()
    def get(self, user_id):
        # 用户请求公文
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return {
                'msg': '用户状态异常！！！'
            }, 400
        # 根据用户id返回所有文章
        return returnAllUserArticlesById(user_id)


class ArticleExampleList(Resource):
    def get(self):
        # 根据类型返回所有的范文
        article_type = request.args.get("type")
        return returnAllExampleArticles(article_type)


api.add_resource(ArticleExampleList, '/examples')
api.add_resource(ArticleUserList, '/articles/<int:user_id>')