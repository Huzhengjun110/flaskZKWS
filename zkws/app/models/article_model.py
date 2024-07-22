from app.extensions import db


class ArticlesModel(db.Model):
    # 用于保存范例文章信息
    __tablename__ = 'model_articles'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(
        db.Enum('新闻', '演讲', '公函', '命令', '议案', '公报', '纪要', '公告', '通告', '意见', '通知', '通报', '报告',
                '请示', '批复', '决议', '决定', '其他'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_by_type(cls, TYPE):
        def to_json(x):
            return {
                'type': x.type,
                'title': x.title,
                'content': x.content,
            }

        return {'articles': list(map(lambda x: to_json(x), cls.query.filter_by(type=TYPE)))}


class UserArticlesModel(db.Model):
    # 用于保存用户的文章信息
    __tablename__ = 'user_articles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(
        db.Enum('新闻', '演讲', '公函', '命令', '议案', '公报', '纪要', '公告', '通告', '意见', '通知', '通报', '报告',
                '请示', '批复', '决议', '决定', '其他'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    updated_time = db.Column(db.DateTime, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_user_id(cls, user_id):
        # 根据用户id返回所有保存的文章
        def to_json(x):
            return {
                'id': x.id,
                'type': x.type,
                'title': x.title,
                'content': x.content,
                'created_time': x.created_time.isoformat(),
                'updated_time': x.updated_time.isoformat()
            }

        return {'Articles': list(map(lambda x: to_json(x), cls.query.filter_by(user_id=user_id)))}
