# 파일명: src/get_token.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# 권한 설정 (메일 보내기 전용)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_token():
    # 1. credentials.json 파일 위치 확인
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(current_dir, 'credentials.json')
    
    if not os.path.exists(cred_path):
        print(f"❌ '{cred_path}' 파일이 없어요! 1단계에서 다운받은 파일을 src 폴더에 넣어주세요.")
        return

    # 2. 구글 로그인 창 띄우기
    flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
    creds = flow.run_local_server(port=0)

    # 3. token.json 저장
    token_path = os.path.join(current_dir, 'token.json')
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print("✅ 인증 성공! 'src/token.json' 파일이 생성되었습니다.")

if __name__ == '__main__':
    get_token()