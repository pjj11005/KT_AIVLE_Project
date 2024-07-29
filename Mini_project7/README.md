## 프로젝트 개요

### 프로제트 요약

- 주제: 에이블스쿨 지원자를 위한 QA챗봇 만들기
- 데이터: 에이블스쿨 홈페이지 Q&A, 조별 데이터 수집
- 중점 사항
    - text 데이터를 vector DB로 만들기
    - GPT 3.5 버전과 연계한 RAG 챗봇 모델 생성
    - 웹 서버와 서비스 구현

### 요구 사항

- 목표
    - 에이블 스쿨 지원자들을 위한 QA 챗봇 서비스
    - AI 모델 + 클라우드 웹 서버 + DB(벡터 DB on SQLite3) + 장고 웹 프레임 워크
    - 구현 범위
        - 개인 : 기본 요구 사항
        - 팀: 기본 + 추가 요구 사항
1. 데이터 수집
    - 질문 + 답변으로 구성시키면 더 좋다
    - 기본 : 에이블 스쿨 홈페이지 Q&A
    - 추가 : 데이터 추가 수
    - 기본 : DB 구성
        - RAG 용 Vector DB
        - 사용 기록 DB
2. 기능 요구사항
    - 질문 답변 기능
        - 기본
            - Open AI 모델 사용
            - Vector DB를 Retriever로 사용
            - 단발성 질문 답변
        - 추가
            - 대화가 이어지도록 구성
            - 정확한 답변을 하기 위한 다양한 시도
    - 사용자 화면
        - 기본
            - 웹과 모바일 모두 접속 가능
            - 단발성 질문, 답변 페이지
        - 추가
            - 질문 답변이 이어지도록 구성 + **세션 안에서 메모리 관리**
    - 관리자 페이지
        - 추가
            - 사용 이력 조회
            - Vector DB 관리 : Vector DB에 추가, 조회 기능
    - 웹 서버
        - 기본
            - 웹 서버에 Vector DB 저장
            - 간단한 방화벽 설정 등으로 IP를 통해서 사이트를 전 세계에 공개
        - 추가
            - 클라우드 환경 구축

## 추가 지식

### API

- 클라이언트 프로그램에게 요청을 받아 서버로 전달 → 서버는 요청을 처리한 후 결과 데이터를 API에 전달 → API가 다시 데이터를 클라이언트로 전달
- Request
    - API 주소 + API Key
    - Request 형식 : 요청 양식
- Response
    - Response 형식 : 결과 양식

### LangChain

- LangChain : 대규모 언어 모델(LLMs)을 활용하여 체인을 구성 → 이 체인을 통해, 복잡한 작업을 자동화하고 쉽게 수행할 수 있도록 돕는 라이브러리
- OpenAI에서 제공하는 모델 사용
    - LLM: gpt-3.5-turbo

### RAG(Retrieval Augmented Generation)

- LLM 생성 방법
    - Modeling
    - Fine-Tuning : 사전 학습된 LLM에, 나의 데이터로 추가 학습
    - RAG : 사전 학습된 LLM에, 나의 데이터로 답변
- LLM with RAG
    1. 사용자 질문 받음
    2. 준비된 정보 DB에서 답변에 필요한 문서 검색
    3. 필요한 문서를 포함한 프롬프트 생성
    4. LLM이 답변 생성하기
- 준비된 정보 DB
    - Vector DB : 대규모 텍스트 데이터 및 임베딩 벡터를 저장하고 검색하는데 사용
    - 질문 벡터와 문서 벡터 유사도 계산 → 유사도가 높은 n개 찾음 → 필요한 문서 포함한 프롬프트 생성
    - Vector DB로 **Chroma DB** 사용
- **Chroma DB: 유사도 점수(Similarity Score)**
    - Cosine Distance 이용
        - Cosine Distance(a, b) = 1 - Cosine Similarity(a, b)
        - **0에 가까울 수록 유사도가 높음**
        - Cosine Similarity(a, b) : 벡터 a, b 사이 cosine 값
- Vector DB 구축 절차(Chroma DB)
    - 텍스트 추출 : Document Loader
        - 다양한 문서(word, pdf, web page 등)로 부터 텍스트 추출하기
    - 텍스트 분할 : Text Splitter
        - chunk 단위로 분할
        - Document 객체로 만들기
    - 텍스트 벡터화 : Text Embedding
    - Vector DB로 저장 : Vector Store
- Chroma DB
    - SQLite3 기반 Vector DB
    - DB Browser for SQLite3로 접속 가능

### Vector DB 생성

- 절차
    - 임베딩 모델 지정
    - Chroma DB 선언: 경로 지정, 임베딩 모델 지정

### Memory

- 이전 질문 답변을 Memory에 저장하고 프롬프트에 포함 → 현재 대화 진행(다시 질문)


## 프로젝트 준비

### 가상환경 준비

- qa_system이라는 가상환경 생성
- python 3.11버전의 가상환경에 사용할 라이브러리 설치(requirements.txt)

### OpenAI API 연결

- API KEY 환경변수 등록

## 프로젝트 내용

### 데이터 수집
1. 에이블 홈페이지 QA, 보도자료, 후기 데이터 수집
2. 수집한 데이터들을 질문과 답변 형식으로 저장하여 데이터 전처리

### 모델 구축
1. 전처리한 데이터 저장하여 RAG 문서로 활용
2. openAI API 활용하여 GPT-3.5-turbo 모델 사용
3. 세션 유지 및 메모리 기능을 통해 사용자의 대화가 유지되도록 구성
4. 에이블 스쿨에 대한 QA챗봇 생성

### 추가 구현
1. Django 기본 admin이 아닌 직접 admin 페이지 생성
2. 미리 질문할만한 요소를 생성하여 쉽게 접근하도록 구현
3. csv파일 업로드하여 DB에 데이터 추가 가능
    - 기존의 데이터와 유사도 비교하여 높으면 입력 안함 

### 서비스 배포
1. AWS 서버를 구축하고 Django를 활용하여 전체적인 프레임워크 구현
2. 서비스 배포

## 느낀점

- RAG, LangChain을 활용한 QA 챗봇 생성 과정을 파악할 수 있었다.
- 데이터 양을 적절히 조절하여 챗봇의 성능을 향상시키는 공부가 필요하다.
- AWS서버에 Django 웹프레임워크로 구축한 서비스 배포 과정을 숙지해야겠다.