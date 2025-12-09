import os
import requests
from dotenv import load_dotenv

# 1. API 키 로드
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"🔑 현재 인식된 API 키: {api_key[:5]}...{api_key[-5:] if api_key else '없음'}")

if not api_key:
    print("❌ API 키가 없습니다! .env 파일을 확인하세요.")
    exit()

# 2. 구글 서버에 '사용 가능한 모델 목록' 직접 요청 (LangChain 안 씀)
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ 구글 서버 연결 성공! 사용 가능한 모델 목록:")
        
        found_flash = False
        for model in data.get('models', []):
            print(f" - {model['name']}")
            if "gemini-1.5-flash" in model['name']:
                found_flash = True
        
        print("\n" + "="*30)
        if found_flash:
            print("🎉 'gemini-1.5-flash' 모델이 목록에 있습니다!")
            print("👉 결론: API 키는 정상입니다. 코드를 수정하면 해결됩니다.")
        else:
            print("😱 목록에 'gemini-1.5-flash'가 없습니다!")
            print("👉 결론: 이 API 키로는 해당 모델을 쓸 수 없습니다. (새 키 발급 필요)")
            
    else:
        print(f"\n❌ 서버 에러 발생! 상태 코드: {response.status_code}")
        print(f"내용: {response.text}")

except Exception as e:
    print(f"\n❌ 연결 실패: {e}")