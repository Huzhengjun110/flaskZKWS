import os
import shutil
import uuid
from datetime import datetime

from flask import send_from_directory
from sqlalchemy import func

from app.models.rag_model import KnowledgeModel, FileModel
from app.models.user_model import UserModel
from app.extensions import db


def createKnowledgeAndFolder(knowledge_name):
    knowledge = KnowledgeModel.query.filter_by(knowledge_name=knowledge_name).first()
    if knowledge:
        return {
                   "code": 400,
                   "msg": "名为{}的知识库已存在".format(knowledge_name)
               }, 400
    # 下面这行代码是根据为用户创建知识库改的，需要传一个用户id的参数，为防止报错，这里就直接用-1占位
    # 在修改过程中，需要为知识库添加一个参数，一个能够访问该知识库问答chat的接口信息，添加在下面，占时以字符串-1占位
    knowledge = KnowledgeModel(-1, knowledge_name, '-1')
    folder_name = knowledge.knowledge_name
    folder_path = os.path.join(os.path.abspath('./'), 'uploads', folder_name)
    os.mkdir(folder_path)
    db.session.add(knowledge)
    db.session.commit()
    return {
               "code": 201,
               "id": knowledge.id,
               "msg": "已新建名为{}的知识库".format(knowledge.knowledge_name)
           }, 201


def updateKnowledgeAndFolder(knowledge_id, new_knowledge_name):
    knowledge = KnowledgeModel.query.filter_by(id=knowledge_id).first()
    if not knowledge:
        return {
                   "code": 400,
                   "msg": "系统不存在id为{}的知识库".format(knowledge_id)
               }, 400
    else:
        old_knowledge_name = knowledge.knowledge_name
        knowledge.knowledge_name = new_knowledge_name
        old_folder_name = old_knowledge_name
        new_folder_name = new_knowledge_name
        old_folder_path = os.path.join(os.path.abspath('./'), 'uploads', old_folder_name)
        new_folder_path = os.path.join(os.path.abspath('./'), 'uploads', new_folder_name)
        os.rename(old_folder_path, new_folder_path)
        db.session.commit()
        return {
                   "code": 201,
                   "msg": "已将名为{}的知识库的名称修改为{}".format(old_knowledge_name, knowledge.knowledge_name)
               }, 201


def getKnowledgeList(knowledge_name):
    query = KnowledgeModel.query
    if knowledge_name:
        query = query.filter(func.lower(KnowledgeModel.knowledge_name).contains(func.lower(knowledge_name)))
    knowledge_list = query.filter_by()
    return {
               "code": 200,
               "msg": "查询成功",
               "knowledge_list": [
                   {
                       "id": item.id,
                       "knowledge_name": item.knowledge_name,
                       "files_count": item.files_count,
                       "ai_model_chat": item.ai_model_chat,
                   } for item in knowledge_list
               ]
           }, 200


def getKnowledgeById(knowledge_id):
    knowledge = KnowledgeModel.query.filter_by(id=knowledge_id).first()
    if knowledge:
        return {
                   "code": 200,
                   "msg": "查询成功",
                   "data": {
                       "id": knowledge.id,
                       "knowledge_name": knowledge.knowledge_name
                   }
               }, 200
    else:
        return {
                   "code": 400,
                   "msg": "查询失败，没有id为{}的知识库".format(knowledge_id)
               }, 400


def deleteKnowledgeById(knowledge_id):
    knowledge = KnowledgeModel.query.filter_by(id=knowledge_id).first()
    if knowledge:
        folder_name = knowledge.knowledge_name
        folder_path = os.path.join(os.path.abspath('./'), 'uploads', folder_name)
        # 删除知识库前还要删除知识库下的所有文件信息
        files_list = FileModel.query.filter_by(knowledge_id=knowledge.id)
        for i in files_list:
            db.session.delete(i)
        # 删除知识库
        db.session.delete(knowledge)
        db.session.commit()
        cleanDir(folder_path)
        os.rmdir(folder_path)
    return {
               "code": 200,
               "msg": "删除成功"
           }, 200


def cleanDir(Dir):  # 声明一个叫cleandir的函数，函数的参数是dir
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


def downloadFileById(file_id):
    file = FileModel.query.filter_by(id=file_id).first()
    if file:
        knowledge = KnowledgeModel.query.filter_by(id=file.knowledge_id).first()
        user = UserModel.query.filter_by(id=knowledge.user_id).first()
        folder_name = user.nickname + "_" + knowledge.knowledge_name
        path = os.path.join(os.path.abspath("./"), 'uploads', folder_name)
        return send_from_directory(path, file.new_file_name, as_attachment=True)
    else:
        return {
                   "code": 400,
                   "msg": "文件不存在"
               }, 400


def uploadFile(user_id, knowledge_name, file):
    knowledge = KnowledgeModel.query.filter_by(knowledge_name=knowledge_name, user_id=user_id).first()
    if not knowledge:
        return {
                   "code": 400,
                   "msg": "上传失败，没有名为{}的知识库".format(knowledge_name)
               }, 400
    try:
        if file.filename == '':
            print("访问参数为空")
        if file:
            original_filename = file.filename
            upload_time = datetime.now()  # 获取当前上传时间
            # 转换为只包含日期的格式
            upload_time = upload_time.date()
            cur_file = FileModel.query.filter_by(knowledge_id=knowledge.id,
                                                 original_file_name=original_filename).first()
            if cur_file:
                print('知识库中已有该文件')
            else:
                # 生成唯一的文件名
                new_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
                user = UserModel.query.filter_by(id=knowledge.user_id).first()
                folder_name = user.nickname + "_" + knowledge.knowledge_name
                file_path = os.path.join(os.path.abspath("./"), 'uploads', folder_name, new_filename)
                file.save(file_path)

                cur_file = FileModel(
                    original_file_name=original_filename,
                    new_file_name=new_filename,
                    knowledge_id=knowledge.id,
                    upload_time=upload_time
                )
                db.session.add(cur_file)
                knowledge.files_count = knowledge.files_count + 1
                db.session.commit()
            print('文件上传完成')
            return {
                "msg": "文件上传完成"
            }
    except Exception as e:
        print('文件上传过程中出错: {}'.format(str(e)))


def deleteFileById(user_id, file_id):
    file = FileModel.query.filter_by(id=file_id).first()
    if file:
        knowledge = KnowledgeModel.query.filter_by(id=file.knowledge_id).first()
        user = UserModel.query.filter_by(id=knowledge.user_id).first()
        if user.id != user_id:
            return {
                       "code": 400,
                       "msg": "权限不足"
                   }, 400
        db.session.delete(file)
        folder_name = user.nickname + "_" + knowledge.knowledge_name
        path = os.path.join(os.path.abspath("./"), 'uploads', folder_name, file.new_file_name)
        os.remove(path)
        knowledge.files_count = knowledge.files_count - 1
        db.session.commit()
    return {
        "code": 200,
        "msg": "删除成功！"
    }


def getFileList(user_id, knowledge_id, file_name):
    knowledge = KnowledgeModel.query.filter_by(id=knowledge_id).first()
    user = UserModel.query.filter_by(id=knowledge.user_id).first()
    if user.id != user_id:
        return {
                   "code": 400,
                   "msg": "权限不足"
               }, 400
    query = FileModel.query
    if file_name != "null":
        query = query.filter(func.lower(FileModel.original_file_name).contains(func.lower(file_name)))
    files = query.filter_by(knowledge_id=knowledge.id)
    return {
               "code": 200,
               "msg": "查询成功",
               "files": [
                   {
                       "id": item.id,
                       "original_file_name": item.original_file_name,
                       "new_file_name": item.new_file_name,
                       "upload_time": item.upload_time.isoformat()[:10],
                       "knowledge_id": knowledge.id
                   } for item in files
               ]
           }, 200
