from .models import ChatLog
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.utils.dateparse import parse_date
from django.db import connections
import datetime
from .forms import UploadFileForm
import csv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, Document

# TODO: 로그인 기능 구현 후 주석 해제
@login_required
def index(request):
    if request.method=='GET':
        result = ChatLog.objects.all().values('timestamp', 'question', 'answer')
        return render(request, 'adminPage/index.html', {'result': result})

    if request.method == 'POST':
        end_date = request.POST.get('end_date', '')
        start_date = request.POST.get('start_date', '')

        if end_date and start_date:
            # 변환할 형식을 정의
            date_format = "%Y-%m-%d"

            # 문자열을 datetime.date 객체로 변환
            end_date = datetime.datetime.strptime(end_date, date_format).date()
            start_date = datetime.datetime.strptime(start_date, date_format).date()

            result = ChatLog.objects.filter(timestamp__date__gte=start_date,
                                             timestamp__date__lte=end_date).values('timestamp', 'question', 'answer')
        else:
            result = ChatLog.objects.all().values('timestamp', 'question', 'answer')

        return render(request, 'adminPage/index.html', {'result': result})
# def chat_view(request):
#     if request.method=='POST':
#         question = request.POST.get('question')
#         answer=generate_answer(question)
#         ChatLog.objects.create(question=question,answer=answer)
#         return JsonResponse({'question': question, 'answer': answer})
#     return render(request)

# def generate_answer(question):
#     return "This is a dummy answer"

def logout_view(request):
    logout(request)
    # 로그아웃 후 처리
    return redirect('login')

def login_view(request):
    print(request.user)
    if request.method == 'GET':
        if (request.user == 'admin'):
            return redirect(settings.ADMIN)
        return render(request, 'adminPage/login.html')

    if request.method == 'POST':
        username = request.POST['id']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_admin:
            login(request, user)

        else:
            error_message = "Invalid username or password."
            return render(request, 'adminPage/login.html', {'error_message': error_message})
    return render(request, 'adminPage/login.html')


def admin_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date=parse_date(start_date)
        end_date=parse_date(end_date)
        admin_list=ChatLog.objects.filter(timestamp__range=(start_date,end_date))
    else:
        admin_list=ChatLog.objects.all()
    return render(request,'adminPage/index.html',{'post_all':admin_list})

# def admin_detail(request,pk):
#     object=get_object_or_404(ChatLog,pk=pk)
#     return render(request,'')


# def admin_update(request,pk):
#     object=get_object_or_404(ChatLog,pk=pk)
#     if request.method=='POST':
#         form=ChatLog(request.POST,instance=object)
#         if form.is_valid():
#             form.save()
#             return redirect('admin_list')
#         else: 
#             form = ChatLog(instance=object)
#         return render(request, 'adminPage/index.html',{'form':form})
    
def admin_delete(request,pk):
    chatlog=get_object_or_404(ChatLog,pk=pk)
    if request.method =="POST":
        chatlog.delete()
        return redirect('admin_list')
    else:
        return render(request,'adminPage/index.html',{'chatlog':chatlog})


    if request.method == 'POST':
        form = ChatLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_list')
    else:
        form = ChatLogForm()
    return render(request, 'create.html', {'form': form})

# 페이지 이동
def contents(request):
    return render(request, 'adminPage/contents.html')

# DB 불러오기
def read_data():
    with connections['chroma'].cursor() as cursor:
        cursor.execute("SELECT * FROM embedding_fulltext_search_content")
        data = cursor.fetchall()
    return data

# DB 조회
def display_data(request):
    if request.method == 'POST':
        data = read_data()
        formatted_data = [{'id': row[0], 'text': row[1]} for row in data]
        return render(request, 'adminPage/contents.html', {'data': formatted_data})
    return render(request, 'adminPage/contents.html')
    
    
def upload_csv_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            
            # CSV 파일이 비어 있는지 확인
            if not any(reader):
                return render(request, 'adminPage/contents.html', {'form': form, 'data': [], 'error': 'CSV 파일이 비어 있습니다.'})
            
            embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
            database = Chroma(persist_directory='./database', embedding_function=embeddings)
            save_meta = []
            save_documents = []
            for row in reader:
                if len(row) < 2:
                    continue  # 올바르지 않은 행 무시
                sim_documents = database.similarity_search_with_score(row[1], k=1)
                if sim_documents:
                    max_score = round(sim_documents[0][1], 5)
                    if max_score > 0.1:
                        save_meta.append(row[0])
                        save_documents.append(row[1])
            
            if not save_documents:
                return render(request, 'adminPage/contents.html', {'form': form, 'data': [], 'error': '저장할 문서가 없습니다.'})
            
            metadata = [{'구분': cat} for cat in save_meta]
            documents = [Document(page_content=save_documents[i], metadata=metadata[i]) for i in range(len(save_documents))]
            
            try:
                x = database.add_documents(documents)
                print(x)
            except Exception as e:
                print(f"Error adding documents: {e}")
                return render(request, 'adminPage/contents.html', {'form': form, 'data': [], 'error': '문서 추가 중 오류가 발생했습니다.'})
            
            return redirect('upload_csv')  # 업로드 후 리디렉션
    else:
        form = UploadFileForm()

    # 데이터베이스에서 데이터를 가져와서 템플릿에 전달
    data = []  # 예: MyModel.objects.all()

    return render(request, 'adminPage/contents.html', {'form': form, 'data': data})