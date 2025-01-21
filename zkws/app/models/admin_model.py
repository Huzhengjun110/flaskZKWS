from app.extensions import db
from passlib.hash import pbkdf2_sha512 as sha512


class AdminModel(db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    type_id = db.Column(db.Integer, nullable=False)

    def __init__(self, username, password, admin_type):
        self.username = username
        self.password = password
        self.type_id = admin_type

    @staticmethod
    def generate_hash(password):
        return sha512.hash(password)

    @staticmethod
    def verify_hash(password, hash_value):
        return sha512.verify(password, hash_value)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class UserTypeModel(db.Model):
    __tablename__ = 'user_type'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(20), nullable=False, unique=True)

    @classmethod
    def getTypeNameById(cls, type_id):
        return cls.query.filter_by(id=type_id).first().type_name
