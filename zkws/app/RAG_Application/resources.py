from datetime import datetime
import json
import os
import shutil
from threading import Thread
import uuid
from flask import Blueprint, Response, current_app, request
from flask_restful import Resource, Api
from app.RAG_Application.db_model import chat_history_model, topic, files, topic_classification
from app.RAG_Application.rag_serverce import get_match_1, get_match_2, get_match_3, get_match_with_file_1, get_match_with_file_2, get_match_with_file_3
from app.RAG_Application.rag_serverce import set_milvus, delete_milvus, chat, get_chat_history_by_topic_id, rag_chat, get_suggest_question
from app.RAG_Application.ai_serverce import QA_chat
from app.extensions import db

bp = Blueprint('home', __name__, url_prefix='/qyrag')
api = Api(bp)

def CleanDir(Dir):  # 声明一个叫cleandir的函数，函数的参数是dir
    if os.path.isdir(Dir):  # os.path.isdir()函数判断dir是否是一个目录，同理os.path.isfile()函数判断是否是一个文件。
        paths = os.listdir(Dir)  # os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表。
        for path in paths:
            filePath = os.path.join(Dir, path)  # os.path.join()方法是，拼接参数里的路径，
            if os.path.isfile(filePath):  # 见第8行
                try:
                    os.remove(filePath)  # 删除
                except os.error:  # 后边这些都看不懂喽
                    print(os.error)
            elif os.path.isdir(filePath):
                if filePath[-4:].lower() == ".svn".lower():
                    continue
                shutil.rmtree(filePath, True)
    return True

class Home(Resource):
    def get(self):
        return {
            "msg": "hello"
        }

class Topic(Resource):
    """
    # 会话管理，会话的查找、创建、删除
    """
    def get(self):
        # 查询并返回所有会话的基本信息
        user_id = request.args.get('user_id')
        try:
            topic_list = topic.query.filter_by(user_id=user_id).all()
            results = []
            for tp_item in topic_list:
                classification = topic_classification.query.filter_by(classification_id=tp_item.classification_id).first()
                results.append({
                    "topic_id": tp_item.id,
                    "topic_name": tp_item.topic_name,
                    "is_RAG": tp_item.is_RAG,
                    "classification_id": tp_item.classification_id,
                    "classification_name":classification.classification_name,
                    "create_time":tp_item.create_time.isoformat()
                })
            return {
                "code": 200,
                "msg": "成功",
                "topic_list": results
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": "服务器内部错误:{}".format(e)
            }, 500
    
    def put(self):
        # 修改会话信息
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        topic_name = data['topic_name']
        classification_id = data.get('classification_id', 1)
        tp = topic.query.filter_by(id=topic_id).first()
        tp.topic_name = topic_name
        tp.classification_id = classification_id
        db.session.commit()
        return{
            "code": 201,
            "msg": "修改会话信息成功",
            "topic": {
                "topic_id": tp.id,
                "topic_name": tp.topic_name,
                "is_RAG": tp.is_RAG,
                "classification_id":tp.classification_id
            }
        }



    
    def post(self):
        # 创建一个会话，包括会话信息、文件目录、
        data = request.get_data()
        data = json.loads(data)
        topic_name = data['topic_name']
        user_id = data['user_id']
        classification_id = data.get('classification_id', 1)
        upload_time = datetime.now()  # 获取时间
        try:
            tp = topic(user_id=user_id, classification_id=classification_id, topic_name=topic_name, is_RAG=0, create_time=upload_time)
            db.session.add(tp)
            db.session.commit()
            return {
                       "code": 201,
                       "msg": "创建会话成功",
                       "id": tp.id
                   }, 201
        except Exception as e:
            return {
                       "code": 500,
                       "msg": "服务器内部错误:{}".format(e)
                   }, 500

    def delete(self):
        """
        删除会话：
        1、删除历史对话记录
        2、删除文件、清除文件信息
        3、删除会话信息
        :return:
        """
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        try:
            # 根据topic_id查询数据库topic表中是否存在该条目
            tp = topic.query.filter_by(id=topic_id).first()
            if tp:
                db.session.delete(tp)
                # 要删除知识库下的所有文件信息
                files_list = files.query.filter_by(topic_id=tp.id)
                for i in files_list:
                    db.session.delete(i)
                db.session.commit()
                
                # 如果为rag还要清除milvus数据内容
                if tp.is_RAG == 1:
                    delete_milvus(tp.id)
                try:
                    # 使用 SQLAlchemy 的 delete 方法结合 filter 进行批量删除
                    result = db.session.query(chat_history_model).filter_by(topic_id=tp.id).delete()
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    raise e
                return {
                    "code": 200,
                    "msg": "删除会话{}成功！".format(tp.topic_name)
                }
            else:
                return {
                    "code": 400,
                    "msg": "参数错误，id为{}的会话不存在".format(topic_id)
                }, 400
        except Exception as e:
            return {
                "code": 500,
                "msg": "服务器内部错误:{}".format(e)
            }, 500

class Topic_Classification(Resource):
    """
    # 会话类型管理，会话类型的查找、创建、删除
    """
    def get(self):
        topic_classification_list = topic_classification.query.filter_by().all()
        results = []
        for classification in topic_classification_list:
            results.append({
                "classification_id": classification.classification_id,
                "classification_name": classification.classification_name
            })
        return {
            "code": 200,
            "msg": "成功",
            "topic_list": results
        }
    def post(self):
        pass
    def delete(self):
        pass

class File(Resource):

    def get(self, topic_id):
        # 请求文件列表
        cur_topic = topic.query.filter_by(id=topic_id).first()
        if cur_topic is None:
            return {
                "code": 400,
                "msg": '参数错误，topic不存在。'
            }, 400
        file_list = files.query.filter_by(topic_id=topic_id)
        return{
            "code": 200,
            "msg": "success",
            "file_list":[
                {
                    "file_id":item.id,
                    "topic_id": item.topic_id,
                    "new_filename": item.new_filename,
                    "original_filename": item.original_filename,
                    "upload_time": item.upload_time.isoformat()[0:10]
                }
                for item in file_list
            ]
        }

    def put(self, topic_id):
        # 生成向量数据库
        # 更改topic.is_rag为1
        cur_topic = topic.query.filter_by(id=topic_id).first()
        if cur_topic is None:
            return {
                "code": 400,
                "msg": '参数错误，topic不存在。'
            }, 400
        try:
            set_milvus(folder=cur_topic)
            cur_topic.is_RAG = 1
            db.session.commit()
            return {
                "code": 200,
                "msg": 'success'
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": '向量数据库生成过程中出错: {}'.format(str(e))
            }, 500

    def post(self, topic_id):
        # 上传文件
        file = request.files['file']
        cur_topic = topic.query.filter_by(id=topic_id).first()
        
        try:
            if file.filename == '' or cur_topic is None:
                return {
                           "code": 400,
                           "msg": "访问参数异常"
                       }, 400
            if file:
                original_filename = file.filename
                upload_time = datetime.now()  # 获取当前上传时间
                # 转换为只包含日期的格式
                upload_time = upload_time.date()
                cur_file = files.query.filter_by(topic_id=cur_topic.id, original_filename=original_filename).first()
                if cur_file:
                    print('文件库中已有该文件')
                else:
                    # 生成唯一的文件名
                    new_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
                    file_path = os.path.join(os.path.abspath("./"), 'uploads', new_filename)
                    file.save(file_path)
                    cur_file = files(
                        original_filename=original_filename,
                        new_filename=new_filename,
                        topic_id=cur_topic.id,
                        upload_time=upload_time
                    )
                    db.session.add(cur_file)
                    db.session.commit()
                return {
                    "code":200,
                    "msg": "文件上传完成"
                }
        except Exception as e:
            return {
                        "code": 500,
                       "msg": '文件上传过程中出错: {}'.format(str(e))
                   }, 500

class RAG_Chat(Resource):
    # 调用大模型，知识召回与问答
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        sender_name = data['sender_name']
        send_text = data['send_text']

        tp = topic.query.filter_by(id=topic_id).first()
        # folder_name = tp.folder_name
        # 先根据folder_name加载历史会话记录
        chat_history_list = get_chat_history_by_topic_id(tp.id)

        response = rag_chat("collection_" + str(topic_id), send_text, chat_history_list)

        
        # 将send_text和response存储起来
        chat_content = chat_history_model(topic_id=tp.id, user_content=send_text, assistant_content=response)
        db.session.add(chat_content)
        db.session.commit()
        return {
            "code": 200,
            "msg": "success",
            "our_str": response
        }

class Chat(Resource):
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        sender_name = data['sender_name']
        send_text = data['send_text']
        tp = topic.query.filter_by(id=topic_id).first()
        # folder_name = tp.folder_name
        # 先根据folder_name加载历史会话记录
        chat_history_list = get_chat_history_by_topic_id(tp.id)
        # 判断当前对话模式
        response = chat(send_text=send_text, chat_history_list=chat_history_list)
        chat_content = chat_history_model(topic_id=tp.id, user_content=send_text, assistant_content=response)
        db.session.add(chat_content)
        db.session.commit()
        return {
            "code": 200,
            "msg": "success",
            "our_str": response
        }

class Suggest_questions(Resource):
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        question = data['question']
        answer = data['answer']
        json_data = get_suggest_question(question, answer)
        return json_data

class Simple_Match(Resource):
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        user_id = data['user_id']
        send_text = data['send_text']
        demand_analysis = get_match_1(send_text=send_text)
        technical_difficulty = get_match_2(send_text=send_text, text=demand_analysis)
        recommended_outcome = get_match_3(send_text=send_text, text=technical_difficulty)
        result = {
            "demand_analysis": demand_analysis,
            "technical_difficulty": technical_difficulty,
            "recommended_outcome": recommended_outcome,
        }
        # 将字典转换为JSON字符串
        additional_info_json = json.dumps(result)
        chat_content = chat_history_model(
            topic_id=topic_id, 
            user_content=send_text, 
            assistant_content=additional_info_json
        )
        db.session.add(chat_content)
        db.session.commit()
        return {
            "code": 200,
            "msg": "success",
            "demand_analysis": demand_analysis,
            "technical_difficulty": technical_difficulty,
            "recommended_outcome": recommended_outcome,
        }
class Simple_Match_With_file(Resource):
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        topic_id = data['topic_id']
        user_id = data['user_id']
        send_text = data['send_text']
        demand_analysis = get_match_with_file_1("collection_" + str(topic_id), send_text=send_text)
        technical_difficulty = get_match_with_file_2("collection_" + str(topic_id), send_text=send_text, text=demand_analysis)
        recommended_outcome = get_match_with_file_3("collection_" + str(topic_id), send_text=send_text, text=technical_difficulty)
        result = {
            "demand_analysis": demand_analysis,
            "technical_difficulty": technical_difficulty,
            "recommended_outcome": recommended_outcome,
        }
        # 将字典转换为JSON字符串
        additional_info_json = json.dumps(result)
        chat_content = chat_history_model(
            topic_id=topic_id, 
            user_content=send_text, 
            assistant_content=additional_info_json
        )
        db.session.add(chat_content)
        db.session.commit()
        return {
            "code": 200,
            "msg": "success",
            "demand_analysis": demand_analysis,
            "technical_difficulty": technical_difficulty,
            "recommended_outcome": recommended_outcome,
        }

class Simple_Match_history(Resource):
    def get(self, topic_id):
        cur_topic = topic.query.filter_by(id=topic_id).first()
        if not cur_topic:
            return {
                "code": 400,
                "msg": "没有id为{}的会话".format(topic_id),
            }, 400
        chat_history = chat_history_model.query.filter_by(topic_id=topic_id).all()
        return {
            "code": 200,
            "msg": "success",
            "data": [
                {
                    "user": item.user_content, 
                    "assistant": json.loads(item.assistant_content)
                } for item in chat_history
            ]
        }

class Topic_history(Resource):
    def get(self, topic_id):
        cur_topic = topic.query.filter_by(id=topic_id).first()
        if not cur_topic:
            return {
                "code": 400,
                "msg": "没有id为{}的会话".format(topic_id),
            }, 400
        chat_history = chat_history_model.query.filter_by(topic_id=topic_id).all()
        return {
            "code": 200,
            "msg": "success",
            "data": [
                {
                    "user": item.user_content, "assistant": item.assistant_content 
                } for item in chat_history
            ]
        }

def background_insert_chat(topic_id, question, text):
    from run import application

    with application.app_context():
        chat_content = chat_history_model(topic_id=topic_id, user_content=question, assistant_content=text)
        db.session.add(chat_content)
        db.session.commit()

class QA_Chat(Resource):
    def post(self):
        """
            流式传输接口
        """
        data = request.get_data()
        data = json.loads(data)
        user_id = data['user_id']
        topic_id = data['topic_id']
        question = data['question']
        chat_history_list = chat_history_model.query.filter_by(topic_id=topic_id).all()
        ret = QA_chat(query=question, chat_history=chat_history_list)
        def predict():
            text=''
            for _token in ret:
                token = _token.content
                js_data = {"code": "200", "msg": "success", "data": token}
                yield f"data: {json.dumps(js_data,ensure_ascii=False)}\n\n"
                text += token
            thread = Thread(target=background_insert_chat, args=(topic_id, question, text))
            thread.start()

        generate = predict()
        return Response(generate, content_type="text/event-stream")

class Update_File_Without_TopicId(Resource):
    def get(self,user_id):
        # 返回所有临时文件的信息
        file_list = files.query.filter_by(user_id=user_id)
        return{
            "code": 200,
            "msg": "success",
            "file_list":[
                {
                    "file_id":item.id,
                    "user_id": item.user_id,
                    "new_filename": item.new_filename,
                    "original_filename": item.original_filename,
                }
                for item in file_list
            ]
        }
    def post(self, user_id):
        try:
            file = request.files['file']
            if file.filename == '':
                return {
                            "code": 400,
                            "msg": "访问参数异常"
                        }, 400
            if file:
                original_filename = file.filename
                upload_time = datetime.now()  # 获取当前上传时间
                # 转换为只包含日期的格式
                upload_time = upload_time.date()
                cur_file = files.query.filter_by(user_id=user_id, original_filename=original_filename).first()
                if cur_file:
                    print('文件库中已有该文件')
                else:
                    # 生成唯一的文件名
                    new_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
                    file_path = os.path.join(os.path.abspath("./"), 'uploads', new_filename)
                    file.save(file_path)
                    cur_file = files(
                        original_filename=original_filename,
                        new_filename=new_filename,
                        user_id=user_id,
                        upload_time=upload_time
                    )
                    db.session.add(cur_file)
                    db.session.commit()
                return {
                    "code":200,
                    "msg": "文件上传完成"
                }
        except Exception as e:
            return {
                        "code": 500,
                       "msg": '文件上传过程中出错: {}'.format(str(e))
                   }, 500
    def delete(self,user_id):
        # 根据用户id删除所有临时文件
        pass

class Create_Topic_With_file_id_list(Resource):
    def post(self):
        data = request.get_data()
        data = json.loads(data)
        file_id_list = data['file_id_list']
        user_id = data['user_id']
        topic_name = data['topic_name']
        upload_time = datetime.now()  # 获取时间
        try:
            tp = topic(user_id=user_id, topic_name=topic_name, is_RAG=1, create_time=upload_time)
            db.session.add(tp)
            db.session.commit()
            for file_id in file_id_list:
                f = files.query.filter_by(user_id=user_id,id=file_id).first()
                print(f)
                if f:
                    f.topic_id = tp.id
                    f.user_id = -1
            db.session.commit()
            return {
                       "code": 201,
                       "msg": "创建会话成功",
                       "id": tp.id
                   }, 201
        except Exception as e:
            return {
                       "code": 500,
                       "msg": "服务器内部错误:{}".format(e)
                   }, 500


api.add_resource(Home, '/')
api.add_resource(Topic, '/topic')
api.add_resource(Topic_Classification, '/topicClassification')
api.add_resource(File, '/file/<int:topic_id>')
api.add_resource(Topic_history, '/history/<int:topic_id>')

api.add_resource(RAG_Chat, '/RAGchat')
api.add_resource(Chat, '/chat')

api.add_resource(QA_Chat, '/qa')
api.add_resource(Suggest_questions, '/question')
api.add_resource(Simple_Match, '/simplematch')
api.add_resource(Simple_Match_With_file, '/simplematchwithfile')
api.add_resource(Simple_Match_history, '/simplematchhistory/<int:topic_id>')

api.add_resource(Update_File_Without_TopicId, '/tempfile/<int:user_id>')
api.add_resource(Create_Topic_With_file_id_list, '/topicwithfile')