import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# API 키 로드
load_dotenv()

class MarketingAgent:
    def __init__(self):
        # 🤖 Gemini 1.5 Flash 모델 설정 (무료, 빠름)
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",  # 최신 라이브러리에서는 이 이름이 맞습니다.
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # 📝 프롬프트: 작가에게 주는 지령서
        self.prompt = PromptTemplate(
            input_variables=["brand", "product_name", "features", "reviews", "persona"],
            template="""
            당신은 {brand}의 전문 카피라이터입니다.
            제공된 [제품 정보]와 [고객 페르소나]를 분석하여, 구매 욕구를 자극하는 개인화 마케팅 메시지(SMS/알림톡)를 작성하세요.

            [고객 페르소나]
            {persona}

            [제품 정보]
            - 브랜드: {brand}
            - 제품명: {product_name}
            - 특징: {features}
            - 실제 고객 리뷰 반응: {reviews}

            [작성 규칙]
            1. **톤앤매너**: {brand} 브랜드 이미지에 맞출 것 (설화수: 우아/정중, 라네즈: 발랄/트렌디).
            2. **구조**: [후킹 문구] -> [공감 및 솔루션] -> [행동 유도] 순서로 작성.
            3. **길이**: 모바일에서 읽기 편하게 3~4문장, 줄바꿈 활용.
            4. **필수**: 고객의 고민(페르소나)을 언급하며 이 제품이 해결책임을 강조. 이모지 적절히 사용.

            [메시지 생성]:
            """
        )

    def generate_message(self, product_info, customer_persona):
        # 체인 연결: 프롬프트 -> LLM -> 문자열출력
        chain = self.prompt | self.llm | StrOutputParser()
        
        # 실제 생성 요청
        response = chain.invoke({
            "brand": product_info['brand'],
            "product_name": product_info['name'],
            "features": product_info['search_text'], 
            "reviews": product_info['metadata'].get('skin_type', '정보 없음'), # 메타데이터 활용
            "persona": customer_persona
        })
        
        return response

if __name__ == "__main__":
    # 테스트 코드
    agent = MarketingAgent()
    print("🤖 작가 에이전트 준비 완료!")