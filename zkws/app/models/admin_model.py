from app.extensions import db
from app.resources.schemas.admin_schema import AdminType
from passlib.hash import pbkdf2_sha512 as sha512


class AdminModel(db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    admin_type = db.Column(db.Enum(AdminType), nullable=False)

    def __init__(self, username, password, admin_type):
        self.username = username
        self.password = password
        self.admin_type = admin_type

    @staticmethod
    def generate_hash(password):
        return sha512.hash(password)

    @staticmethod
    def verify_hash(password, hash_value):
        return sha512.verify(password, hash_value)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
