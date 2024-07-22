from flask_restful import reqparse


new_article_data = reqparse.RequestParser()
new_article_data.add_argument('type', required=True, help='Type cannot be blank')
new_article_data.add_argument('title', required=False)
new_article_data.add_argument('content', required=False)

update_articles_data = reqparse.RequestParser()
update_articles_data.add_argument('article_id', type=int, required=True)
update_articles_data.add_argument('type', required=True)
update_articles_data.add_argument('title')
update_articles_data.add_argument('content')