from app.extensions import db


class OrderModel(db.Model):
    # 存储订单信息
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String(255))
    quantity = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_orderNumber(cls, order_number):
        return cls.query.filter_by(order_number=order_number).first()


class ProductsModel(db.Model):
    # 存储商品信息
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.UnicodeText, nullable=False)
    price_per_use = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String(255), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False)

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'product_id': x.product_id,
                'name': x.name,
                'description': x.description,
                'price_per_use': float(x.price_per_use),
                'status': x.status
            }

        return {'products': list(map(lambda x: to_json(x), cls.query.filter_by()))}


class PaymentsModel(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False)
    payment_url = db.Column(db.UnicodeText, nullable=False)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_orderNumber(cls, order_number):
        return cls.query.filter_by(order_number=order_number).first()
