from flask_restful import reqparse


# 自定义验证函数，确保字段不为空字符串
def not_empty_string(value, name):
    if not value or value.strip() == "":
        raise ValueError(f"{name} cannot be blank")
    return value


# 创建商品订单时,前端需要提供的信息
order_parser = reqparse.RequestParser()
order_parser.add_argument(
    "product_id",
    type=int,
    help='product_id cannot be blank',
    required=True,
)
order_parser.add_argument(
    "quantity",
    type=int,
    help='quantity cannot be blank',
    required=True,
)

# 创建支付订单时，前端需要提供的信息
payment_parser = reqparse.RequestParser()
payment_parser.add_argument(
    "order_number",
    type=lambda x: not_empty_string(x, 'order_number'),
    help='order_number cannot be blank',
    required=True
)
payment_parser.add_argument(
    "subject",
    type=lambda x: not_empty_string(x, 'subject'),
    help='subject cannot be blank',
    required=True
)
payment_parser.add_argument(
    "payment_method",
    type=lambda x: not_empty_string(x, 'payment_method'),
    help='payment_method cannot be blank',
    required=True
)
payment_parser.add_argument(
    "return_url",
    type=lambda x: not_empty_string(x, 'return_url'),
    help='return_url cannot be blank',
    required=True
)
