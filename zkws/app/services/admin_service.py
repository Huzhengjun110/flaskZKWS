from sqlalchemy import func

from app.models.admin_model import AdminModel, UserTypeModel
from app.models.article_model import ArticlesModel
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token


def CreateAdminAccountService(username, password, type_id):
    # 新建管理员账户
    print()
    admin = AdminModel(username, AdminModel.generate_hash(password), type_id)
    admin.save_to_db()
    return {
        'code': 201,
        'msg': 'success'
    }, 201


def AdminLoginService(username, password):
    # 管理员登录
    admin = AdminModel.query.filter_by(username=username).first()
    if admin:
        if AdminModel.verify_hash(password, admin.password):
            # 管理员创建token需要添加user_type
            type_name = UserTypeModel.getTypeNameById(type_id=AdminModel.type_id)
            access_token = create_access_token(identity=admin.id, additional_claims={'role': type_name})
            refresh_token = create_refresh_token(admin.id)
            return {
                'msg': 'successful',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'msg': 'wrong password'}
    else:
        return {'msg': 'wrong username'}


def getAdminAccountById(account_id):
    cur_admin = AdminModel.query.filter_by(id=account_id).first()
    if cur_admin:
        admin_type = UserTypeModel.query.filter_by(id=cur_admin.user_type).first().type_name
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "id": cur_admin.id,
                "username": cur_admin.username,
                "admin_type": admin_type
            }
        }
    else:
        return {
                   "code": 400,
                   "msg": "未找到id为{}的管理员".format(account_id)
               }, 400


def getAdminAccountList(page, page_size, admin_name):
    query = AdminModel.query
    if admin_name:
        query = query.filter(func.lower(AdminModel.username).contains(func.lower(admin_name)))
    admins = query.paginate(page=page, per_page=page_size)
    return {
        "articles": [
            {
                "id": admin.id,
                "username": admin.username,
                "user_type": UserTypeModel.getTypeNameById(admin.type_id)
            } for admin in admins
        ],
        "total_pages": admins.pages,
        "current_page": admins.page,
        "page_size": admins.per_page
    }


def UpdateAdminInformationService(update_account_id, username, password, admin_type):
    # 更新管理员账户信息
    current_account = AdminModel.query.filter_by(id=update_account_id).first()
    if current_account:
        current_account.user_type = admin_type
        current_account.username = username
        current_account.password = password
        user_type = UserTypeModel.getTypeNameById(current_account.user_type)
        db.session.commit()
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "id": current_account.id,
                "username": current_account.username,
                "admin_type": user_type
            }
        }
    else:
        return {
                   "code": 400,
                   "msg": "未找到id为{}的管理员".format(update_account_id)
               }, 400


def insertArticleIntoDatabase(article_title, article_type, article_content):
    new_article = ArticlesModel(article_title, article_type, article_content)
    db.session.add(new_article)
    db.session.commit()
    return {
               "code": 201,
               "msg": "新建范文成功"
           }, 201


def deleteArticleById(article_id):
    cur_article = ArticlesModel.query.filter_by(id=article_id).first()
    if cur_article:
        db.session.delete(cur_article)
        db.session.commit()
        return {
                   "code": 200,
                   "msg": "删除范文成功"
               }, 200
    else:
        return {
                   "code": 400,
                   "msg": "数据库中不存在id为{}的范文".format(article_id)
               }, 400


def getArticleById(article_id):
    cur_article = ArticlesModel.query.filter_by(id=article_id).first()
    if cur_article:
        return {
                   "code": 200,
                   "msg": "查询成功",
                   "article_info": {
                       "type": cur_article.type,
                       "title": cur_article.title,
                       "content": cur_article.content
                   }
               }, 200
    else:
        return {
                   "code": 400,
                   "msg": "数据库中不存在id为{}的范文".format(article_id)
               }, 400


def updateArticleById(article_id, article_title, article_type, article_content):
    cur_article = ArticlesModel.query.filter_by(id=article_id).first()
    if cur_article:
        cur_article.type = article_type
        cur_article.title = article_title
        cur_article.content = article_content
        db.session.commit()
        return {
                   "code": 200,
                   "msg": "修改成功",
               }, 200
    else:
        return {
                   "code": 400,
                   "msg": "数据库中不存在id为{}的范文".format(article_id)
               }, 400


def getArticlesList(article_type, article_title, page, page_size):
    query = ArticlesModel.query
    if article_title:
        query = query.filter(func.lower(ArticlesModel.title).contains(func.lower(article_title)))
    if article_type:
        query = query.filter_by(type=article_type)
    articles = query.paginate(page=page, per_page=page_size)
    return {
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "type": article.type,
                "content": article.content
            } for article in articles
        ],
        "total_pages": articles.pages,
        "current_page": articles.page,
        "page_size": articles.per_page
    }
