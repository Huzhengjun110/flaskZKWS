from flask import Blueprint
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.resources.schemas.user import register_parser, login_parser
from app.services.user_service import register, login, getUserInformation

bp = Blueprint('users', __name__, url_prefix='/users')
api = Api(bp)


class UserRegister(Resource):
    def post(self):
        data = register_parser.parse_args()
        return register(data['nickname'], data['phone'], data['email'], data['password'])


class UserLogin(Resource):
    def post(self):
        data = login_parser.parse_args()
        return login(data['account'], data['password'])


class UserInformation(Resource):
    @jwt_required()
    def get(self, user_id):
        identity_user = get_jwt_identity()
        if identity_user == user_id:
            return getUserInformation(user_id)
        else:
            return {
                       'msg': '账户异常'
                   }, 400

    @jwt_required()
    def put(self, user_id):
        pass


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def get(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserInformation, '/<int:user_id>')
api.add_resource(TokenRefresh, '/refresh')
