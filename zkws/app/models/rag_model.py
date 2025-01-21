from app.extensions import db


class KnowledgeModel(db.Model):
    # 知识库数据模型
    __tablename__ = 'knowledge_db'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    knowledge_name = db.Column(db.String(255), nullable=False)
    files_count = db.Column(db.Integer, nullable=False)
    ai_model_chat = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, name, ai_model_chat, count=0):
        self.user_id = user_id
        self.ai_model_chat = ai_model_chat
        self.knowledge_name = name
        self.files_count = count


class FileModel(db.Model):
    # 知识库数据模型
    __tablename__ = 'file_db'

    id = db.Column(db.Integer, primary_key=True)
    knowledge_id = db.Column(db.Integer, nullable=False)
    original_file_name = db.Column(db.String(255), nullable=False)
    new_file_name = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
