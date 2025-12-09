import os
import shutil
import time
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 👇👇👇 여기를 수정했어! (만능 임포트 구문) 👇👇👇
try:
    # main.py에서 실행할 때 (거실에서 부를 때)
    from src.data_loader import load_product_data
except ImportError:
    # vector_db.py를 직접 실행할 때 (방 안에서 부를 때)
    from data_loader import load_product_data
# 👆👆👆 여기까지 수정 👆👆👆


# ... (나머지 코드는 그대로 두면 돼) ...
load_dotenv()

CHROMA_PATH = "chroma_db"

class ProductVectorDB:
    def __init__(self):
        print("📥 임베딩 모델 로딩 중... (내 컴퓨터 CPU 사용)")
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.db = None # 처음엔 연결 안 함 (파일 잠금 방지)

    def create_vector_db(self):
        """
        기존 DB를 삭제하고 새로 만듭니다.
        """
        # 1. 기존 DB가 있다면 강제 삭제
        if os.path.exists(CHROMA_PATH):
            # 혹시 연결되어 있다면 끊기
            self.db = None 
            print("🧹 기존 DB 삭제 시도...")
            
            # 윈도우 파일 잠금 풀릴 때까지 잠시 대기 후 삭제
            try:
                shutil.rmtree(CHROMA_PATH)
                print(f"✨ 삭제 완료: {CHROMA_PATH}")
            except PermissionError:
                print("⚠️ 파일이 잠겨있어서 강제 삭제를 시도합니다...")
                time.sleep(1) # 1초 숨 고르기
                try:
                    shutil.rmtree(CHROMA_PATH) # 재시도
                except Exception as e:
                    print(f"❌ 삭제 실패 (그냥 덮어쓰기 진행): {e}")

        # 2. 데이터 로드
        raw_data = load_product_data()
        if not raw_data:
            print("❌ 데이터가 없습니다.")
            return

        documents = []
        for item in raw_data:
            doc = Document(
                page_content=item["search_text"],
                metadata=item["metadata"]
            )
            documents.append(doc)

        # 3. 벡터 DB 생성 및 저장 (이제 연결!)
        print("🔮 데이터를 벡터로 변환 및 저장 중...")
        self.db = Chroma.from_documents(
            documents=documents,
            embedding=self.embedding_model,
            persist_directory=CHROMA_PATH
        )
        print(f"✅ 벡터 DB 구축 완료! 총 {len(documents)}개 데이터 저장됨.")

    def load_db(self):
        """
        이미 만들어진 DB를 불러올 때 씀
        """
        if self.db is None:
            self.db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=self.embedding_model
            )

    def search(self, query, k=3):
        # DB가 로드 안 되어 있으면 로드
        self.load_db()
        
        print(f"\n🔎 검색 쿼리: '{query}'")
        results = self.db.similarity_search_with_score(query, k=k)
        return results

if __name__ == "__main__":
    vector_db = ProductVectorDB()
    
    # 1. 생성 (기존 거 지우고 새로 만듦)
    vector_db.create_vector_db()
    
    # 2. 검색 테스트
    test_query = "피부가 너무 건조하고 당겨서 고민이야. 엄마 선물로 좋을만한 거?"
    results = vector_db.search(test_query)
    
    print(f"\n🏆 검색 결과 Top 3:")
    for doc, score in results:
        print(f"--- [유사도 거리: {score:.4f}] ---")
        print(doc.page_content[:100] + "...")