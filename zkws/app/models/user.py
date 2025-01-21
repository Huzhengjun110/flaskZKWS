from app.extensions import db
from passlib.hash import pbkdf2_sha512 as sha512
from app.models.order import ProductsModel


class UserModel(db.Model):
    # 用户表，4个主要字段
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def generate_hash(password):
        return sha512.hash(password)

    @staticmethod
    def verify_hash(password, hash_value):
        return sha512.verify(password, hash_value)


class RevokedTokenModel(db.Model):
    # 存用户主动退出登录的token，约等于一个黑名单
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class UserCountsModel(db.Model):
    # 存储用户当前接口的剩余使用次数
    __tablename__ = 'user_counts_table'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    counts = db.Column(db.Integer, nullable=False)

    @classmethod
    def find_by_user_id(cls, user_id):
        # 根据用户id返回用户剩余接口数量
        def to_json(x):
            return {
                'product_id': x.product_id,
                'counts': x.counts,
            }

        return list(map(lambda x: to_json(x), cls.query.filter_by(user_id=user_id)))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def newUserCounts(cls, user_id):
        # 为该用户初始化每个接口的使用次数
        products = ProductsModel.query.all()
        for product in list(products):
            count = cls(user_id=user_id, product_id=product.product_id, counts=500)
            cls.save_to_db(count)
