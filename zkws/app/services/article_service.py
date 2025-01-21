import datetime
from app.extensions import db

from app.models.article_model import ArticlesModel, UserArticlesModel


def returnAllExampleArticles(Type):
    return ArticlesModel.return_by_type(Type)


def returnAllUserArticlesById(user_id):
    return UserArticlesModel.find_by_user_id(user_id)


def createUserArticle(user_id, article_type, title, content):
    new_user_article = UserArticlesModel(
        type=article_type,
        title=title,
        content=content,
        user_id=user_id,
        created_time=datetime.datetime.now(),
        updated_time=datetime.datetime.now()
    )
    try:
        new_user_article.save_to_db()
        return {
                   "message": "Save article successful",
                   "type": new_user_article.type,
                   "title": new_user_article.title,
                   "content": new_user_article.content,
                   "created_time": new_user_article.created_time.isoformat()
               }, 201
    except Exception as e:
        return {'message': f'Error saving article: {str(e)}'}, 500


def updateUserArticle(article_id, article_type, title, content):
    article = UserArticlesModel.query.filter_by(id=article_id).first()
    article.type = article_type
    article.title = title
    article.content = content
    db.session.commit()
    return {
        "message": "Save article successful",
        "type": article.type,
        "title": article.title,
        "content": article.content,
        "updated_time": article.updated_time.isoformat()
    }, 201


def deleteUserArticles(user_id, article_id):
    article = UserArticlesModel.query.filter_by(id=article_id).first()
    if user_id != article.user_id:
        return {
            "message": "权限不足，无法删除不是别人的历史文档",
        }, 401
    else:
        db.session.delete(article)
        db.session.commit()
        return {
            "message": "删除文档成功",
        }, 201
