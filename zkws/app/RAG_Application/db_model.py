from app.extensions import db


# 数据库模型
class files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(50))
    new_filename = db.Column(db.String(50))
    topic_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    upload_time = db.Column(db.DATE)


class chat_history_model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer)  # 话题的id
    user_content = db.Column(db.TEXT)  # user说的实际内容
    assistant_content = db.Column(db.TEXT)  # assistant说的实际内容


class topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    classification_id = db.Column(db.Integer)
    topic_name = db.Column(db.String(255))
    is_RAG = db.Column(db.Integer)
    create_time = db.Column(db.DATE)

class topic_classification(db.Model):
    classification_id = db.Column(db.Integer, primary_key=True)
    classification_name = db.Column(db.String(255))
