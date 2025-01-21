from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

AI_chat = ChatOpenAI(
    model="qwen",  # 使用的模型
    openai_api_key="default",  # API 密钥
    openai_api_base='http://172.20.19.121:8094/v1',  # API 基础 URL
    streaming=True,
    stop=['<|im_end|>']  # 停止符
)

def QA_chat(query, chat_history):
    chat_history_list = []
    for item in chat_history:
        chat_history_list.extend((HumanMessage(content=item.user_content),AIMessage(content=item.assistant_content)))
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        """You are a helpful assistant."""
    )
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        """
            human message:{query}
        """
    )
    history_message_prompt = MessagesPlaceholder(variable_name="chat_history")
    full_chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        history_message_prompt,
        human_message_prompt
    ])
    print(chat_history_list)
    chat_chain = full_chat_prompt|AI_chat
    ret = chat_chain.stream({"query": query, "chat_history": chat_history_list})
    return ret