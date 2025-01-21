from flask_restful import reqparse
import re
from werkzeug.exceptions import BadRequest


def username(username_str):
    """
    检查用户名是否有效
    :param username_str: 用户名字符串
    :return: 如果有效返回True，否则抛出BadRequest异常
    """
    if 2 <= len(username_str) <= 20 and username_str.isalnum():
        return username_str
    else:
        raise BadRequest("Invalid username. It must be 2-20 characters long and contain only letters and numbers.")


def password(password_str):
    """
    检查密码是否有效
    :param password_str: 密码字符串
    :return: 如果有效返回True，否则抛出BadRequest异常
    """
    if len(password_str) >= 8 and re.search(r'[A-Za-z]', password_str) and re.search(r'[0-9]', password_str):
        return password_str
    else:
        raise BadRequest(
            "Invalid password. It must be at least 8 characters long and contain both letters and numbers.")


def adminData():
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username', dest='username',
        type=username,
        required=True,
    )
    parser.add_argument(
        'password', dest='password',
        type=password,
        required=True,
    )
    parser.add_argument(
        'type_id', dest='type_id',
        type=int,
    )
    args = parser.parse_args()
    return args
