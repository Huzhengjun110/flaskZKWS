from app.models.admin_model import AdminModel
from app.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token


def CreateAdminAccountService(current_account_id, username, password, admin_type):
    current_account = AdminModel.query.filter_by(id=current_account_id).first()
    if current_account and current_account == 'super_admin':
        admin = AdminModel(username, AdminModel.generate_hash(password), admin_type)
        admin.save_to_db()
        return {'msg': 'successful'}
    else:
        return {'msg': '账户权限不足'}


def AdminLoginService(username, password):
    admin = AdminModel.query.filter_by(username=username).first()
    if admin:
        if AdminModel.verify_hash(password, admin.password):
            access_token = create_access_token(admin.id)
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


def UpdateAdminInformationService(current_account_id, update_account_id, username, password, admin_type):
    # 更新管理员账户信息
    current_account = AdminModel.query.filter_by(id=current_account_id).first()
    if current_account and current_account.admin_type == 'super_admin':
        update_account = AdminModel.query.filter_by(id=update_account_id).first()
        if not update_account:
            return {'msg': '意外的错误，要修改的账户id不在数据库中'}
        update_account.username = username
        update_account.password = AdminModel.generate_hash(password)
        update_account.admin_type = admin_type
        db.session.commit()
        return {'msg': 'successful'}
    else:
        return {'msg': '账户权限不足'}
