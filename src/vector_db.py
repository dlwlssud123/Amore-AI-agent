import os
import chromadb
from chromadb.utils import embedding_functions
from data_loader import load_product_data 

# 1. 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, 'chroma_db')

# 2. 임베딩 모델 (한국어 지원)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

def get_client():
    return chromadb.PersistentClient(path=db_path)

def init_db(force_reset=False):
    """DB 초기화 및 데이터 적재"""
    client = get_client()
    
    try:
        cols = client.list_collections()
        col_names = [c.name for c in cols]
    except:
        col_names = []

    if force_reset and "cosmetics" in col_names:
        print("🔄 [DB] 데이터 갱신 중...")
        client.delete_collection("cosmetics")
    
    collection = client.get_or_create_collection(
        name="cosmetics", 
        embedding_function=sentence_transformer_ef
    )

    if collection.count() == 0:
        products = load_product_data()
        if products:
            ids = [str(i) for i in range(len(products))]
            docs = [p['search_text'] for p in products]
            metas = [p['metadata'] for p in products]
            collection.add(ids=ids, documents=docs, metadatas=metas)
            print(f"🎉 [DB] {len(ids)}개 데이터 적재 완료!")
    
    return collection

def search_products(query: str, limit: int = 5):
    """
    [핵심 복원] 사용자가 업로드한 파일 기반의 검색 로직
    - 검색어가 너무 짧으면 빈 리스트 반환
    - DB 연결 실패 시 자동 복구 시도
    """
    if not query or len(query.strip()) < 2:
        return []

    client = get_client()
    try:
        collection = client.get_collection(name="cosmetics", embedding_function=sentence_transformer_ef)
    except:
        collection = init_db()

    # DB가 비어있으면 다시 채우기
    if collection.count() == 0:
        collection = init_db(force_reset=True)

    try:
        # n_results로 개수 제한 (기본 5개)
        results = collection.query(query_texts=[query], n_results=limit)
        
        if not results['documents'] or not results['documents'][0]:
            return []
            
        # 메타데이터 리스트 반환
        return results['metadatas'][0]

    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        return []

def search_best_product(query):
    """1개만 추천할 때 사용"""
    results = search_products(query, limit=1)
    return results[0] if results else None