import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'products.csv')

def load_product_data():
    """CSV 파일을 읽어와서 검색용 텍스트와 메타데이터로 변환"""
    if not os.path.exists(DATA_PATH):
        print(f"❌ [Data Loader] 파일 없음: {DATA_PATH}")
        return []

    try:
        # utf-8-sig로 한글 깨짐 방지, 에러 라인 무시
        df = pd.read_csv(DATA_PATH, encoding='utf-8-sig', on_bad_lines='skip')
        
        products = []
        for _, row in df.iterrows():
            # 데이터 결측치(NaN) 방지용 안전 처리
            brand = str(row.get('brand', ''))
            name = str(row.get('product_name', ''))
            features = str(row.get('features', ''))
            skin_type = str(row.get('skin_type', ''))
            price = str(row.get('price', '0'))

            # 검색용 텍스트 (AI가 이 내용을 보고 찾음)
            ingredients = str(row.get('ingredients', ''))
            search_text = f"[{brand}] {name}\n특징: {features}\n성분: {ingredients}\n추천: {skin_type}"
            
            product_info = {
                "search_text": search_text,
                "metadata": {
                    "brand": brand,
                    "name": name,
                    "price": price,
                    "skin_type": skin_type,
                    "description": features
                }
            }
            products.append(product_info)
            
        print(f"✅ [Data Loader] {len(products)}개 데이터 로드 완료")
        return products

    except Exception as e:
        print(f"❌ [Data Loader] 로드 중 에러: {e}")
        return []
