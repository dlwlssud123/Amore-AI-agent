import os
from src.vector_db import ProductVectorDB
from src.generator import MarketingAgent

def main():
    print("=" * 50)
    print("🚀 AGENT 10: 초개인화 마케팅 메시지 생성기 가동")
    print("=" * 50)

    # 1. 시스템 초기화 (DB 로드 & 작가 섭외)
    print("⚙️ 시스템 로딩 중...")
    try:
        vector_db = ProductVectorDB() # 검색 담당
        writer = MarketingAgent()     # 작문 담당
        print("✅ 시스템 준비 완료!\n")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        print("💡 팁: .env 파일에 GOOGLE_API_KEY가 있는지 확인하세요.")
        return

    # 2. 사용자 입력 (실제로는 웹에서 받겠지만, 지금은 터미널에서)
    print("🎯 타겟 고객 정보를 입력해주세요.")
    # 예시 입력값 (엔터 치면 이거 씀)
    default_persona = "30대 직장인 여성, 최근 야근으로 피부가 푸석하고 탄력이 떨어져서 고민임. 비싼 거라도 확실한 효과 원함."
    
    persona_input = input(f"고객 페르소나 (엔터 시 기본값 사용): ")
    target_persona = persona_input if persona_input.strip() else default_persona
    
    print(f"\n📋 [입력된 페르소나]: {target_persona}")

    # 3. RAG 검색 (Retrieval)
    print("\n🔍 고객에게 딱 맞는 제품을 검색 중입니다...")
    # 고객 페르소나 내용을 쿼리로 날려서 가장 적합한 제품 1개를 찾음
    search_results = vector_db.search(target_persona, k=1)
    
    if not search_results:
        print("❌ 적합한 제품을 찾지 못했습니다.")
        return

    # 가장 유사도 높은 제품 정보 추출
    best_product_doc, score = search_results[0]
    
    # Document 객체에서 정보 파싱 (metadata에 저장해둔 정보 꺼내기)
    best_product_info = {
        "brand": best_product_doc.metadata['brand'],
        "name": best_product_doc.metadata['name'],
        "search_text": best_product_doc.page_content,
        "metadata": best_product_doc.metadata
    }

    print(f"💡 [추천 제품 발견]: {best_product_info['brand']} - {best_product_info['name']}")
    
    # 4. 메시지 생성 (Generation)
    print("\n✍️ AI 카피라이터가 메시지를 작성 중입니다...")
    message = writer.generate_message(best_product_info, target_persona)

    # 5. 최종 결과 출력
    print("\n" + "=" * 50)
    print("💌 [최종 생성된 마케팅 메시지]")
    print("=" * 50)
    print(message)
    print("=" * 50)

if __name__ == "__main__":
    main()