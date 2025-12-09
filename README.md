친구들이 이 파일 하나만 보면 **"환경 설정부터 실행까지"** 한 번에 끝낼 수 있도록 정리했어.
**복사해서 `README.txt` 또는 `README.md` 파일로 저장해서 공유해 줘\!**

(친구들이 헷갈리지 않게 우리가 겪었던 시행착오들—PATH 설정, API 키 등—을 꼼꼼하게 적어뒀어.)

-----

# 📋 AGENT 10: 개발 환경 설정 및 실행 가이드

이 프로젝트는 **RAG(검색 증강 생성) 기반 마케팅 메시지 자동 생성기**입니다.
아모레몰 제품 데이터를 학습하고, 구글 Gemini를 이용해 광고 문자를 작성합니다.

## 🛠 0. 필수 준비물 (설치 전 확인\!)

1.  **VS Code** 설치
2.  **Miniconda (또는 Anaconda)** 설치
      * ⚠️ **중요:** 설치할 때 옵션 중 **`Add Miniconda3 to my PATH environment variable`** 체크박스를 **반드시 체크**해야 합니다. (빨간 글씨 무시하고 체크\!)
      * 체크 안 하면 터미널에서 `conda` 명령어가 안 먹힙니다.

-----

## 🚀 1. 가상환경 세팅 (터미널 명령어)

VS Code를 켜고 터미널(`Ctrl` + `` ` ``)을 연 뒤, 아래 명령어들을 순서대로 입력하세요.

### (1) 파이썬 가상환경 만들기

```bash
# 'agent10'이라는 이름의 방을 만들고 Python 3.10 버전을 깝니다.
conda create -n agent10 python=3.10
```

*(중간에 Proceed? [y/n] 나오면 `y` 입력 후 엔터)*

### (2) 가상환경 접속하기

```bash
conda activate agent10
```

👉 **확인:** 터미널 프롬프트 맨 앞에 `(agent10)` 이라고 뜨면 성공\!

-----

## 📦 2. 라이브러리 설치

프로젝트 폴더 최상단에 `requirements.txt` 파일을 만들고 아래 내용을 복사해 붙여넣으세요. (이미 있다면 건너뛰기)

**📄 requirements.txt 내용:**

```text
# LLM & AI Core
langchain
langchain-community
langchain-core
langchain-openai
langchain-google-genai
langchain-huggingface

# Vector DB & Data
chromadb
pandas
numpy
sentence-transformers

# Utils
python-dotenv
jupyter
beautifulsoup4
```

**설치 명령어 실행:**

```bash
pip install -r requirements.txt
```

*(에러 없이 설치가 완료될 때까지 기다려주세요.)*

-----

## 🔑 3. API 키 설정 (Google Gemini)

우리는 무료인 **Google Gemini API**를 사용합니다.

1.  **[Google AI Studio](https://aistudio.google.com/app/apikey)** 에 접속해서 **Create API key** 클릭.
2.  프로젝트 폴더 맨 바깥에 `.env` 라는 파일을 만드세요. (파일명 앞에 점 `.` 필수\!)
3.  `.env` 파일 안에 아래와 같이 적고 저장하세요.

<!-- end list -->

```ini
GOOGLE_API_KEY=여기에_복사한_키_붙여넣기
```

*(주의: 이 파일은 절대 깃허브에 올리면 안 됨\!)*

-----

## 📂 4. 프로젝트 폴더 구조

파일들이 제자리에 있는지 확인하세요.

```text
AGENT-10/
├── 📂 data/
│   └── products.csv       # 제품 데이터 (엑셀 파일 대체)
├── 📂 src/
│   ├── data_loader.py     # 데이터 읽어오는 코드
│   ├── vector_db.py       # 벡터 DB 구축 및 검색 (HuggingFace 사용)
│   └── generator.py       # 메시지 생성 (Gemini 사용)
├── .env                   # API 키 저장소
├── requirements.txt       # 설치 목록
└── README.txt             # 지금 보고 있는 파일
```

-----

## 🏃‍♂️ 5. 실행 테스트

터미널에서 아래 순서대로 실행해보세요.

### (1) 벡터 DB 구축 및 검색 테스트

데이터를 읽어서 AI가 검색할 수 있게 변환합니다.

```bash
python src/vector_db.py
```

> **성공 시:** `✅ 벡터 DB 구축 완료!` 메시지가 뜨고 검색 결과가 출력됨.

### (2) 메시지 생성 테스트 (Gemini)

검색된 정보를 바탕으로 마케팅 문구를 작성합니다.

```bash
python src/generator.py
```

> **성공 시:** `💌 [생성된 메시지]` 아래에 광고 문구가 출력됨.

-----

## 🆘 자주 묻는 질문 (Troubleshooting)

**Q. `conda : 용어 'conda'을(를) 인식할 수 없습니다.` 라고 떠요.**
A. 미니콘다 설치할 때 `PATH` 체크를 안 해서 그래요.

1.  미니콘다 삭제 후 재설치 (설치 시 체크박스 꼭 확인\!)
2.  또는 윈도우 검색창에 **"Anaconda Prompt"** 검색해서 거기서 명령어 입력하세요.

**Q. `ModuleNotFoundError` 에러가 떠요.**
A. `conda activate agent10`을 안 해서 그렇거나, `pip install -r requirements.txt`가 제대로 안 된 겁니다. 다시 실행해보세요.

**Q. API 에러가 나요.**
A. `.env` 파일에 키가 제대로 들어갔는지, 저장(`Ctrl+S`)은 했는지 확인하세요.
