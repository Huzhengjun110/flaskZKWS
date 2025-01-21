import time

from app.models.user_model import UserModel, UserCountsModel
from app.models.order_model import ProductsModel
from flask_jwt_extended import create_access_token, create_refresh_token


def login(account, password):
    # 查找用户
    current_user = UserModel.find_by_phone(account)
    if not current_user:
        current_user = UserModel.find_by_email(account)
        if not current_user:
            return {'message': '账户或密码输入错误！'}, 404
    # 验证密码
    if not UserModel.verify_hash(password, current_user.password):
        time.sleep(1)  # 增加延迟以防止暴力破解
        return {'message': '账户或密码输入错误！'}, 404
    # 创建JWT令牌
    try:
        access_token = create_access_token(identity=current_user.id)
        refresh_token = create_refresh_token(identity=current_user.id)
        return {
                   "message": "Login successful",
                   "user_information": {
                       "user_id": current_user.id,
                       "nickname": current_user.nickname,
                       "phone": current_user.phone,
                       "email": current_user.email
                   },
                   "token": {
                       "access_token": access_token,
                       "refresh_token": refresh_token
                   }
               }, 200
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(str(e))}, 500


def register(nickname, phone, email, password):
    # 检查手机号和邮箱是否已存在
    if UserModel.find_by_phone(phone):
        return {'message': '手机号已被注册!'}, 400
    if UserModel.find_by_email(email):
        return {'message': '邮箱已被注册！'}, 400
    # 创建新用户
    new_user = UserModel(
        nickname=nickname,
        phone=phone,
        email=email,
        password=UserModel.generate_hash(password)
    )
    try:
        new_user.save_to_db()
        # 创建新用户后，同时为每个用户创建对应的余量信息
        UserCountsModel.newUserCounts(new_user.id)
        # 创建JWT令牌
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        return {
                   "message": "Register successful",
                   "user_information": {
                       "user_id": new_user.id,
                       "nickname": new_user.nickname,
                       "phone": new_user.phone,
                       "email": new_user.email
                   },
                   "token": {
                       "access_token": access_token,
                       "refresh_token": refresh_token
                   }
               }, 201
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(str(e))}, 500


def getUserInformation(user_id):
    # 根据用户id返回用户信息，包括基本信息与接口剩余情况信息。
    user = UserModel.query.filter_by(id=user_id).first()
    user_counts = UserCountsModel.query.filter_by(user_id=user_id)

    def to_json(x):
        product = ProductsModel.query.filter_by(product_id=x.product_id).first()
        return {
            'product_id': product.product_id,
            'name': product.name,
            'counts': x.counts,
            'status': product.status,
            'price_per_use': float(product.price_per_use)
        }

    counts = list(map(lambda x: to_json(x), user_counts))
    data = {
               "user_info": {
                   "nickname": user.nickname,
                   "phone": user.phone,
                   "email": user.email
               },
               "user_counts": counts
           }, 200
    return data
