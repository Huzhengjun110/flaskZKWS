from flask_restful import reqparse

model_data = reqparse.RequestParser()
model_data.add_argument('sender_name', required=True)
model_data.add_argument('send_text', required=True)


