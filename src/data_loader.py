import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'products.csv')

def load_product_data():
    print(f"📂 데이터 로딩 중... 경로: {DATA_PATH}")
    
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ 총 {len(df)}개의 제품 데이터를 불러왔습니다.")
        
        products = []
        for _, row in df.iterrows():
            search_text = f"[{row['brand']}] {row['product_name']} \n특징: {row['features']} \n리뷰: {row['reviews']} \n추천타입: {row['skin_type']}"
            
            product_info = {
                "brand": row['brand'],
                "name": row['product_name'],
                "price": row['price'],
                "category": row['category'],
                "search_text": search_text,
                # 🔥 여기가 중요! 메타데이터에 브랜드랑 이름을 꼭 넣어줘야 함
                "metadata": {
                    "brand": row['brand'],
                    "name": row['product_name'],
                    "price": row['price'],
                    "skin_type": row['skin_type']
                }
            }
            products.append(product_info)
            
        return products

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return []

if __name__ == "__main__":
    load_product_data()