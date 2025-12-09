import pandas as pd
import os

# 현재 파일(data_loader.py)의 위치를 기준으로 데이터 파일 경로 찾기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 프로젝트 루트
DATA_PATH = os.path.join(BASE_DIR, 'data', 'products.csv')

def load_product_data():
    """
    CSV 파일에서 제품 데이터를 로드하여 정리된 딕셔너리 리스트로 반환합니다.
    """
    print(f"📂 데이터 로딩 중... 경로: {DATA_PATH}")
    
    try:
        # CSV 읽기
        df = pd.read_csv(DATA_PATH)
        
        # 데이터가 잘 읽혔는지 확인
        print(f"✅ 총 {len(df)}개의 제품 데이터를 불러왔습니다.")
        
        products = []
        for _, row in df.iterrows():
            # RAG 검색에 잘 걸리도록 텍스트를 하나로 합침 (중요!)
            # 형식: [브랜드] 제품명 - 특징 (피부타입)
            search_text = f"[{row['brand']}] {row['product_name']} \n특징: {row['features']} \n리뷰: {row['reviews']} \n추천타입: {row['skin_type']}"
            
            product_info = {
                "brand": row['brand'],
                "name": row['product_name'],
                "price": row['price'],
                "category": row['category'],
                "search_text": search_text, # 이게 벡터 DB에 들어갈 핵심 내용
                "metadata": { # 나중에 필터링할 때 쓸 정보들
                    "price": row['price'],
                    "skin_type": row['skin_type']
                }
            }
            products.append(product_info)
            
        return products

    except FileNotFoundError:
        print("❌ 에러: data/products.csv 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

# 테스트 코드 (이 파일을 직접 실행했을 때만 동작)
if __name__ == "__main__":
    data = load_product_data()
    if data:
        print("\n🔎 첫 번째 데이터 미리보기:")
        print(data[0]['search_text'])