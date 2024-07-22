import os
import time
import random
from app.models.order_model import OrderModel, PaymentsModel, ProductsModel
from app.models.user_model import UserCountsModel
from alipay import AliPay
import datetime
from app.extensions import db

# 支付宝付款配置
with open(os.path.join(os.getcwd(), 'app/key/RSA2048_app_private_key.txt'), "r") as f:  # 打开应用私钥文件
    app_private_key_string = f.read()  # 读取文件
with open(os.path.join(os.getcwd(), 'app/key/alipay_public_key.txt'), "r") as f:  # 打开支付宝公钥文件
    alipay_public_key_string = f.read()  # 读取文件
alipay = AliPay(
    appid="9021000138625769",  # 支付宝沙箱应用的id
    app_private_key_string=app_private_key_string,  # 应用私钥
    alipay_public_key_string=alipay_public_key_string,  # alipay 公钥
    app_notify_url=None,  # 回调地址
    sign_type="RSA2",  # 签名算法
    debug=True,  # 请求来到支付宝沙箱
)


# 生成订单号
def generate_order_number():
    timestamp = int(time.time() * 1000)  # 获取当前时间戳，单位为毫秒
    random_num = random.randint(1000, 9999)  # 生成4位随机数
    order_id = f"O{timestamp}{random_num}"  # 组合成订单号，前缀O表示订单
    return order_id


# 生成订单
def createOrder(user_id, product_id, quantity):
    # 查找商品
    product = ProductsModel.query.filter_by(product_id=product_id).first()
    # 创建订单
    new_order = OrderModel(
        order_number=generate_order_number(),
        product_id=product_id,
        user_id=user_id,
        total_amount=product.price_per_use*quantity,
        status="Pending",  # 默认是已下单，待处理
        quantity=quantity,
        created_time=datetime.datetime.now(),
        updated_time=datetime.datetime.now()
    )
    try:
        new_order.addToDatabase()
        # 返回的主要信息是生成的订单号
        return {
                   "order_number": new_order.order_number,
                   "user_id": new_order.user_id,
                   "product_id": new_order.product_id,
                   "quantity": new_order.quantity,
                   "total_price": float(new_order.total_amount),
                   "status": new_order.status,
                   "created_at": new_order.created_time.isoformat()
               }, 201
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(str(e))}, 500


# 创建支付订单
def createPayment(subject, order_number, payment_method, return_url, user_id=None, amount=None):
    # 根据订单号查询该订单
    order = OrderModel.find_by_orderNumber(order_number)
    if not order:
        return {
                   'message': '该订单不存在'
               }, 400
    if PaymentsModel.find_by_orderNumber(order_number):
        return {
                   'message': '该订单已存在支付订单'
               }, 400
    # 生成支付地址  成功后会返回一个地址 也就是订单支付地址
    order_url = alipay.api_alipay_trade_page_pay(
        subject=subject,  # 订单项目名
        out_trade_no=order_number,  # 订单号
        total_amount=float(order.total_amount),  # 订单价格
        return_url=return_url,
        notify_url=None
    )
    alipay_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?"
    pay_url = alipay_url + order_url
    # 创建支付订单 并存入数据库
    new_payment = PaymentsModel(
        order_number=order_number,
        payment_method=payment_method,
        status="Pending",  # 默认是已生成订单，待处理
        created_time=datetime.datetime.now(),
        updated_time=datetime.datetime.now(),
        payment_url=pay_url
    )

    try:
        # 将支付订单存入数据库
        new_payment.addToDatabase()
    except Exception as e:
        return {'message': 'Something went wrong: {}'.format(str(e))}, 500

    return {
               "order_number": order_number,
               "user_id": order.user_id,
               "amount": float(order.total_amount),
               "payment_method": payment_method,
               "status": new_payment.status,
               "created_at": new_payment.created_time.isoformat(),
               "pay_url": pay_url
           }, 201


# 确认支付完成 执行相应业务
def checkPayment(order_number):
    # 先根据订单号查找本地的订单数据
    order = OrderModel.query.filter_by(order_number=order_number).first()
    payments = PaymentsModel.query.filter_by(order_number=order_number).first()
    if order.status != "Pending" or payments.status != "Pending":
        return {
            'msg': order.status
        }

    result = alipay.api_alipay_trade_query(out_trade_no=order_number)
    if result.get("trade_status", "") == "TRADE_SUCCESS":
        # 查询成功后，首先更改商品订单和支付订单的状态，然后为用户添加api接口使用次数

        order.status = "已支付"
        payments.status = "已支付"
        # 查询订单用户的使用次数
        user_counts = UserCountsModel.query.filter_by(user_id=order.user_id, product_id=order.product_id).first()
        user_counts.counts += order.quantity
        db.session.commit()
        return {
            'message': 'successful'
        }
    else:
        return {
            'message': '支付状态异常'
        }


# 用户请求订单列表
def getOrderList(user_id):
    # 根据user_id在orders表里查该用户所有的订单
    order_list = OrderModel.query.filter_by(user_id=user_id)

    def to_json(x):
        return {
            'order_number': x.order_number,
            'user_id': x.user_id,
            'quantity': x.quantity,
            'total_price': float(x.total_amount),
            'status': x.status,
            'created_time': x.created_time.isoformat()
        }

    data_list = list(map(lambda x: to_json(x), order_list))
    return {
        "orders": data_list
    }
