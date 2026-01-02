import os
import chromadb
from chromadb.utils import embedding_functions
from data_loader import load_product_data 

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, 'chroma_db')

# 임베딩 모델 (한국어 지원)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

def get_client():
    return chromadb.PersistentClient(path=db_path)

def init_db(force_reset=False):
    """DB를 초기화하고 데이터를 채워넣는 함수"""
    client = get_client()
    
    # 기존 컬렉션 확인
    try:
        cols = client.list_collections()
        col_names = [c.name for c in cols]
    except:
        col_names = []

    # 강제 리셋 요청이 있거나, DB가 꼬였을 때 삭제 후 재생성
    if force_reset and "cosmetics" in col_names:
        print("🔄 [DB] 기존 데이터를 삭제하고 새로 만듭니다...")
        client.delete_collection("cosmetics")
    
    # 컬렉션 생성
    collection = client.get_or_create_collection(
        name="cosmetics", 
        embedding_function=sentence_transformer_ef
    )

    # 데이터가 0개면 무조건 로드 시도
    if collection.count() == 0:
        print("📦 [DB] 데이터가 비어있어 로딩을 시작합니다...")
        products = load_product_data()
        
        if not products:
            print("❌ [DB] 로드할 데이터가 없습니다! (products.csv 확인 필요)")
            return None

        # 배치 단위로 추가 (안정성 향상)
        ids = [str(i) for i in range(len(products))]
        docs = [p['search_text'] for p in products]
        metas = [p['metadata'] for p in products]

        collection.add(ids=ids, documents=docs, metadatas=metas)
        print(f"🎉 [DB] 총 {len(ids)}개 제품 데이터 적재 완료!")
    
    return collection

def search_best_product(query):
    """검색 함수 (오류 발생 시 자동 복구 기능 포함)"""
    client = get_client()
    
    try:
        collection = client.get_collection(name="cosmetics", embedding_function=sentence_transformer_ef)
        # 검색 시도 전 데이터 개수 체크
        if collection.count() == 0:
            print("⚠️ [Search] DB가 비어있습니다. 초기화를 시도합니다.")
            collection = init_db(force_reset=True)
            
    except Exception as e:
        print(f"⚠️ [Search] DB 연결 오류({e}). 초기화를 시도합니다.")
        collection = init_db(force_reset=True)

    # 검색 실행
    if collection and collection.count() > 0:
        results = collection.query(query_texts=[query], n_results=1)
        if results['documents'] and results['documents'][0]:
            return results['metadatas'][0][0]
            
    print("❌ [Search] 검색 결과가 없습니다.")
    return None