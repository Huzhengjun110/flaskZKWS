import json
import os
import re
from langchain.schema import HumanMessage, AIMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import ModelScopeEmbeddings
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage
from app.RAG_Application.db_model import chat_history_model, files
# 初始化embeddings模型和chat模型
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = ModelScopeEmbeddings(model_id='iic/nlp_corom_sentence-embedding_chinese-base')
AI_chat = ChatOpenAI(
    model="qwen",  # 使用的模型
    openai_api_key="default",  # API 密钥
    openai_api_base='http://172.20.19.121:8094/v1',  # API 基础 URL
    stop=['<|im_end|>']  # 停止符
)

def knowledge_recall(db_name, send_text):
    """
    根据知识库名称进行知识召回
    :param db_name:
    :param send_text:
    :return:
    """
    # 加载Milvus向量库，用于知识召回
    connection_args = {"host": "172.20.19.231", "port": "19530"}
    vector_db = Milvus(
        embedding_function=embeddings,
        collection_name=db_name,
        connection_args=connection_args,
        drop_old=False
    )
    knowledge_list = vector_db.similarity_search(send_text)
    return knowledge_list

def set_prompt(knowledge_list, send_text, chat_history_list):
    """
    利用langchain构建prompt
    :param knowledge_list: 知识库信息
    :param send_text: 用户提问
    :param chat_history_list: 历史对话信息
    :return: prompt 构建好的prompt
    """
    system_message_template = """你是一个专业的企业能力评估师，可以结合背景文档回答用户提出的问题。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)

    history_message_prompt = MessagesPlaceholder(variable_name="chat_history")

    human_message_template = """
    以下是背景文档的详细内容：
    {document_text}

    问题：{query}
    """
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)

    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        history_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        document_text=[item.page_content for item in knowledge_list],
        query=send_text,
        chat_history=chat_history_list
    ).to_messages()
    return Prompt

def set_prompt_QA(send_text, chat_history_list):
    system_message_template = """你是一个专业的企业能力评估师，可以回答用户提出的问题。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户：{query}
    """
    history_message_prompt = MessagesPlaceholder(variable_name="chat_history")
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        history_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        query=send_text,
        chat_history=chat_history_list
    ).to_messages()
    return Prompt

def rag_chat(db_name, send_text, chat_history_list):
    """
    分为两步：
    1、根据db_name和send_text进行rag知识召回；
    2、将召回的知识、用户发送的信息、用户的历史问答记录一起交给大模型进行回答。
    :param db_name:知识库的名称
    :param send_text:用户发送的信息
    :param chat_history_list:历史问答记录
    :return:
    """
    knowledge_list = knowledge_recall(db_name, send_text)
    prompt = set_prompt(knowledge_list, send_text, chat_history_list)
    response = AI_chat.invoke(prompt)
    return response.content

def chat(send_text, chat_history_list):
    prompt = set_prompt_QA(send_text=send_text, chat_history_list=chat_history_list)
    response = AI_chat.invoke(prompt)
    return response.content

def set_milvus(folder):
    folder_path = os.path.join(os.path.abspath("./"), 'uploads')
    file_list = files.query.filter_by(topic_id=folder.id).all()
    if file_list:
        all_files = [os.path.join(folder_path, f.new_filename) for f in file_list if os.path.isfile(os.path.join(folder_path, f.new_filename))]
        chunks_small = []
        for file_path in all_files:
            pdf_loader = PyPDFLoader(file_path, extract_images=False)
            chunks = pdf_loader.load_and_split(text_splitter=RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10))
            chunks_small.extend(chunks)
        connection_args = {"host": "172.20.19.231", "port": "19530"}
        vector_db = Milvus.from_documents(
            chunks_small,
            embedding=embeddings,
            collection_name="collection_"+str(folder.id),
            connection_args=connection_args,
            drop_old=True,
        )

def delete_milvus(td_id):
    from pymilvus import Milvus
    connection_args = {"host": "172.20.19.231", "port": "19530"}
    # 要删除的集合名称
    collection_name = "collection_" + str(td_id)
    # 创建 Milvus 连接对象
    milvus_client = Milvus(
        embedding_function=None,
        collection_name=collection_name,
        connection_args=connection_args
    )
    # 删除集合
    milvus_client.drop_collection(collection_name)

def get_chat_history_by_topic_id(topic_id):
    """
    根据topic返回该topic下的所有对话内容
    :return:经过id排序的topic
    """
    chat_history = chat_history_model.query.filter_by(topic_id=topic_id).all()
    # 构建历史会话记录
    chat_history_list = []
    for i in chat_history[-10:]:
        chat_history_list.extend((HumanMessage(content=i.user_content), AIMessage(content=i.assistant_content)))
    return chat_history_list

def get_suggest_question(question, answer):
    prompt = """
                你是一个善于提出问题的助手，可以根据问答内容生成三个延申问题。
                The output should be formatted as a JSON instance that conforms to the JSON schema below.
                output format:
                {
                    "questions_list": [
                        {"question_one":"question content"},
                        {"question_two":"question content"},
                        {"question_three":"question content"}
                    ]
                }
            """+"""
                问答内容：
                问题：{0}
                回答：{1}
                输出的json为:
             """.format(question, answer)
    recommendations = AI_chat.invoke(prompt).content
    json_string = re.search(r'\{.*\}', recommendations, re.DOTALL).group(0)
    data = json.loads(json_string)  # 解析JSON字符串
    return data

def set_match_prompt_1(send_text):
    """
    设置简洁匹配的第一部分，根据用户的问题生成需求分析
    """
    system_message_template = """你可以根据用户的问题识别用户需求，并给出需求分析。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    需求分析要包括技术目标和主要的技术挑战。
    需求分析：
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=send_text,
    ).to_messages()
    return Prompt
def get_match_1(send_text):
    """
    生成简洁匹配的第一部分需求分析
    """
    prompt = set_match_prompt_1(send_text=send_text)
    response = AI_chat.invoke(prompt)
    return response.content
def set_match_prompt_2(user_text, text):
    """
    设置简洁匹配的第二部分，根据用户的问题和需求分析生成技术难点
    """
    system_message_template = """你可以根据用户的问题以及问题的需求分析，并列出实现该需求的技术难点"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    需求分析：{text}
    技术难点：
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=user_text,
        text=text
    ).to_messages()
    return Prompt
def get_match_2(send_text, text):
    """
    生成简洁匹配的第二部分技术难点
    """
    prompt = set_match_prompt_2(send_text, text)
    response = AI_chat.invoke(prompt)
    return response.content
def set_match_prompt_3(send_text, text):
    """
    设置简洁匹配的第三部分，根据用户的问题和模型生成的技术难点生成相关的推荐成果
    """
    system_message_template = """你可以根据用户的问题以及问题的技术难点，并提供匹配的科技成果和相应的团队。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    技术难点：{text}
    推荐成果：
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=send_text,
        text=text
    ).to_messages()
    return Prompt
def get_match_3(send_text, text):
    """
    生成简洁匹配的第三部分推荐成果
    """
    prompt = set_match_prompt_3(send_text, text)
    response = AI_chat.invoke(prompt)
    return response.content
def marge_match(text1,text2,text3):
    """融合所用模型回答并润色"""
    system_message_template = """你是一个善于对解决方案进行文字润色的写作能手，能够将方案以严谨、准确的形式进行润色，要求去除与解决方案无关的语句。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    需求分析：{text1}
    技术难点：{text2}
    推荐成果：{text3}
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        text1=text1,
        text2=text2,
        text3=text3
    ).to_messages()
    response = AI_chat.invoke(Prompt)
    return response.content

def get_match_with_file_1(db_name, send_text):
    system_message_template = """你可以根据用户的问题识别用户需求，依据背景资料给出需求分析。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    背景资料：{document_text}
    需求分析要包括技术目标和主要的技术挑战。
    需求分析：
    """
    knowledge_list = knowledge_recall(db_name, send_text)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=send_text,
        document_text=[item.page_content for item in knowledge_list]
    ).to_messages()
    print(Prompt)
    response = AI_chat.invoke(Prompt)
    return response.content

def get_match_with_file_2(db_name, send_text, text):
    system_message_template = """你可以根据用户的问题以及问题的需求分析，依据背景资料列出实现该需求的技术难点"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    需求分析：{text}
    背景资料：{document_text}
    技术难点：
    """
    knowledge_list = knowledge_recall(db_name, text)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=send_text,
        text=text,
        document_text=[item.page_content for item in knowledge_list]
    ).to_messages()
    response = AI_chat.invoke(Prompt)
    return response.content

def get_match_with_file_3(db_name, send_text, text):
    system_message_template = """你可以根据用户的问题以及问题的技术难点，依据背景资料提供匹配的科技成果和相应的团队。"""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
    human_message_template = """
    用户问题：{send_text}
    技术难点：{text}
    背景资料：{document_text}
    推荐成果：
    """
    knowledge_list = knowledge_recall(db_name, text)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_template)
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt
    ])
    Prompt = chat_prompt.format_prompt(
        send_text=send_text,
        text=text,
        document_text=[item.page_content for item in knowledge_list]
    ).to_messages()
    response = AI_chat.invoke(Prompt)
    return response.content