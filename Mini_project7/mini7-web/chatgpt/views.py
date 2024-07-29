from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django import forms
from django.urls import reverse
from django.utils import timezone
from adminPage.models import ChatLog

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.prompts import PromptTemplate

import pandas as pd
import json
import uuid
import requests

# Create your views here.

# DB에서 가져오기
# documents = DBbook.objects.all()
# for document in documents :
#     print(document.id)
#     print(document.info)

# Chroma 데이터베이스 초기화 - 사전에 database가 완성 되어 있다는 가정하에 진행 - aivleschool_qa.csv 내용이 저장된 상태임
embeddings = OpenAIEmbeddings(model = "text-embedding-ada-002", encode='utf-8')
database = Chroma(persist_directory = "./database", embedding_function = embeddings)

# documents = [Document(page_content=text) for text in df.values]
# database.add_documents(documents)

#chatgpt API 및 lang chain을 사용을 위한 선언
llm = ChatOpenAI(model="gpt-3.5-turbo")
k = 7
retriever = database.as_retriever(search_kwargs={"k": k})
    
# 프롬프트
template = '''
당신은 AIVLE School 담장자 입니다. 아래 대화 내용을 참고하여 질문에 대한 답변을 성실하게 해주세요.

{context}

<대화내용>
{chat_history}

<질문>
{question}
'''
custom_prompt = PromptTemplate.from_template(template)

# 메모리
chat_memory = dict()

def index(request):
    message = request.GET.get('message', '')
    context = {'message': message}
    return render(request, 'gpt/index.html', context)

def chat(request):
    print("chat")
    #post로 받은 question (index.html에서 name속성이 question인 input태그의 value값)을 가져옴
    query = request.POST.get('message')

    # session_id = request.session.get('session_id', str(uuid.uuid4()))
    # request.session['session_id'] = session_id
    if not request.session.session_key :
        request.session.create()

    if request.method == 'GET':
        # 응답을 보여주기 위한 html 선택 (위에서 처리한 context를 함께 전달)
        return render(request, 'gpt/result.html', context)
    if not isinstance(query, str):
        return JsonResponse({"error": "Invalid input"}, status=400)

    try:
        # 메모리 부여
        if request.session.session_key not in chat_memory :
            print('new memory')
            chat_memory[request.session.session_key] = ConversationBufferMemory(memory_key="chat_history",
                                                                                input_key="question",
                                                                                output_key="answer",
                                                                                human_prefix="지원자",
                                                                                ai_prefix="AIVLE School 담장자",
                                                                                return_messages=True)

        qa = ConversationalRetrievalChain.from_llm(llm=llm,
                                                   retriever=retriever,
                                                   memory=chat_memory[request.session.session_key],
                                                   output_key="answer",
                                                   combine_docs_chain_kwargs={'prompt' : custom_prompt},
                                                   return_source_documents=True)

        result = qa(query)
        response = result['answer']
        # print(request.session.session_key, chat_memory[request.session.session_key])

        # 대화 내용 저장
        # temp = Qna.objects.create(sid=request.session.session_key, question=query, answer=response)
        # temp.save()
        Logging = ChatLog.objects.create(question=query, answer=response)
        Logging.save()
    except Exception as e:
        print('Error Info : ', e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'response': response})