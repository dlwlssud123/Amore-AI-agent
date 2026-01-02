import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # 👈 여기가 수정되었습니다!

def send_email(to_email, subject, body):
    try:
        # 1. 토큰 불러오기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token.json')
        
        if not os.path.exists(token_path):
            return False, "❌ 'token.json'이 없습니다. get_token.py를 먼저 실행해주세요."

        creds = Credentials.from_authorized_user_file(token_path)
        
        # 2. Gmail API 서비스 연결
        service = build('gmail', 'v1', credentials=creds)
        
        # 3. 메일 내용 구성
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        
        # 4. 전송 (base64 인코딩 필요)
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={'raw': raw}).execute()
        
        return True, "✅ 전송 성공"
        
    except Exception as e:
        return False, f"❌ 전송 실패: {e}"

# 테스트
if __name__ == "__main__":
    # 본인 이메일로 테스트 해보세요
    print(send_email("dlwlssud123@naver.com", "성공!", "구글 API로 보낸 메일입니다."))