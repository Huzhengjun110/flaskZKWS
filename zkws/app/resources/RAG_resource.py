import requests
from flask import Blueprint, request, json
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rag_service import *

bp = Blueprint('rag', __name__, url_prefix='/rag')
api = Api(bp)


def getRequestKnowledge_name():
    """
    通过json数据获取知识库名称
    :return:
    """
    parser = reqparse.RequestParser()
    parser.add_argument('knowledge_name', dest='knowledge_name', required=True)
    folder_info_data = parser.parse_args()
    return folder_info_data.knowledge_name


class FoldersResource(Resource):
    @jwt_required()
    def get(self, folder_id):
        # 根据folder_id返回知识库详细信息
        return getKnowledgeById(folder_id)

    @jwt_required()
    def put(self, folder_id):
        # 根据folder_id修改知识库信息
        new_knowledge_name = getRequestKnowledge_name()
        if len(new_knowledge_name.strip()) == 0:
            return {
                       "code": 400,
                       "msg": "知识库名称没有包含有效字符"
                   }, 400
        return updateKnowledgeAndFolder(folder_id, new_knowledge_name)

    @jwt_required()
    def delete(self, folder_id):
        # 根据folder_id删除知识库信息
        return deleteKnowledgeById(folder_id)


class FoldersListResource(Resource):
    @jwt_required()
    def get(self):
        # 按query对知识库进行条件查询
        knowledge_name = request.args.get('knowledge_name', type=str)
        return getKnowledgeList(knowledge_name)

    @jwt_required()
    def post(self):
        # 为用户添加知识库
        knowledge_name = getRequestKnowledge_name()
        if len(knowledge_name.strip()) == 0:
            return {
                       "code": 400,
                       "msg": "知识库名称没有包含有效字符"
                   }, 400
        return createKnowledgeAndFolder(knowledge_name)


class FilesResource(Resource):
    # 文件管理被禁了暂时不用管
    def get(self, file_id):
        # 根据id下载文件
        return downloadFileById(file_id)

    @jwt_required()
    def delete(self, file_id):
        # 根据id删除文件
        user_id = get_jwt_identity()
        return deleteFileById(user_id, file_id)


class FilesListResource(Resource):
    # 文件管理被禁了暂时不用管
    @jwt_required()
    def get(self):
        # 请求文件列表
        knowledge_id = request.args.get('knowledge_id')
        file_name = request.args.get("file_name")
        user_id = get_jwt_identity()
        return getFileList(user_id, knowledge_id, file_name)

    @jwt_required()
    def post(self):
        # 上传文件
        user_id = get_jwt_identity()
        knowledge_name = request.args.get('knowledge_name')
        file = request.files['file']
        return uploadFile(user_id, knowledge_name, file)


class RAG_Chat(Resource):
    @jwt_required()
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        sender_name = data['sender_name']
        send_text = data['send_text']
        ai_chat = data['chat_name']
        print(ai_chat)

        response = requests.post('http://172.20.19.121:8093/' + ai_chat,
                                 data={"send_text": send_text, "sender_name": sender_name})
        our_str = response.json()
        return {
            "code": 200,
            "msg": "success",
            "our_str": our_str
        }


api.add_resource(FoldersResource, '/folders/<int:folder_id>')
api.add_resource(FoldersListResource, '/folders')

api.add_resource(FilesResource, '/files/<int:file_id>')
api.add_resource(FilesListResource, '/files')

api.add_resource(RAG_Chat, '/chat')
