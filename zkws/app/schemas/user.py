from flask_restful import reqparse

# 自定义验证函数，确保字段不为空字符串
def not_empty_string(value, name):
    if not value or value.strip() == "":
        raise ValueError(f"{name} cannot be blank")
    return value

# 注册时所需的参数
register_parser = reqparse.RequestParser(trim=True)
register_parser.add_argument(
    'nickname',
    type=lambda x: not_empty_string(x, 'nickname'),
    help='Nickname cannot be blank',
    required=True)
register_parser.add_argument(
    'phone',
    type=lambda x: not_empty_string(x, 'phone'),
    help='Phone cannot be blank',
    required=True)
register_parser.add_argument(
    'email',
    type=lambda x: not_empty_string(x, 'email'),
    help='Email cannot be blank',
    required=True)
register_parser.add_argument(
    'password',
    type=lambda x: not_empty_string(x, 'password'),
    help='Password cannot be blank',
    required=True)

# 登录时所需的参数变量
login_parser = reqparse.RequestParser()
login_parser.add_argument(
    'account',
    type=str,
    required=True,
    help='Account is required')
login_parser.add_argument(
    'password',
    type=str,
    required=True,
    help='Password is required')