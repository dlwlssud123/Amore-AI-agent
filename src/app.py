import streamlit as st
import os
import json
import time
import requests
import pandas as pd
from collections import Counter
from vector_db import init_db, search_best_product
from generator import generate_marketing_copy
from dotenv import load_dotenv
from sender import send_email

# --- [초기 설정] ---
load_dotenv()
st.set_page_config(page_title="Glow Code", page_icon="✨", layout="wide")

if 'db_initialized' not in st.session_state:
    # 앱 시작 시 DB 강제 최신화 (CSV 반영)
    with st.spinner("데이터베이스 동기화 중..."):
        init_db(force_reset=True)
        st.session_state['db_initialized'] = True

if 'messages' not in st.session_state:
    st.session_state['messages'] = {}

# --- [유틸리티 함수] ---
def get_weather(city="Daegu"):
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key: return f"📍 {city} | ☀️ 24°C (API키 미설정)"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric&lang=kr"
        data = requests.get(url).json()
        return f"📍 {city} | 🌡️ {int(data['main']['temp'])}°C {data['weather'][0]['description']}"
    except: return f"📍 {city} | ☁️ 날씨 정보 없음"

def get_weekly_forecast(city="Daegu"):
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key: return "(주간 예보 없음)"
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={key}&units=metric&lang=kr"
        data = requests.get(url).json()
        forecast = []
        for item in data['list']:
            if "12:00:00" in item['dt_txt']:
                date = item['dt_txt'][5:10]
                temp = int(item['main']['temp'])
                desc = item['weather'][0]['description']
                forecast.append(f"{date}({desc}/{temp}도)")
        return ", ".join(forecast[:3])
    except: return "(예보 오류)"

def get_users():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

# --- [UI 레이아웃] ---
weather_info = get_weather("Daegu")
col1, col2 = st.columns([3, 1])
with col1: st.title("✨ Glow Code AI Marketer")
with col2: st.info(weather_info)
st.divider()

left, center, right = st.columns([1, 2.5, 1.2], gap="large")

# 1. 왼쪽: 설정 및 분석
with left:
    st.subheader("🛠️ 전략 설정")
    with st.container(border=True):
        mode = st.radio("모드 선택", ["모드 1: 개인화 맞춤", "모드 2: 제품 교육", "모드 3: 날씨/시즌"])
        st.write("---")
        st.checkbox("신규 가입 환영", value=True)
        st.checkbox("재구매 유도")
    
    st.write("")
    with st.popover("📊 실시간 분석 리포트", use_container_width=True):
        st.write("### 📈 Customer Insights")
        users = get_users()[:10]
        if users:
            df = pd.DataFrame(users)
            st.bar_chart(df['skin_type'].value_counts(), color="#FF9AA2")
            all_concerns = [c for u in users for c in u.get('concerns', [])]
            top_concern = Counter(all_concerns).most_common(1)[0][0]
            st.success(f"💡 AI Tip: 현재 **'{top_concern}'** 고민이 가장 많습니다!")

# 2. 중앙: 메시지 생성
with center:
    st.subheader("✉️ 메시지 생성 대시보드")
    
    if st.button("🚀 10명 일괄 생성 시작", type="primary", use_container_width=True):
        bar = st.progress(0)
        users = get_users()[:10]
        weekly_weather = get_weekly_forecast("Daegu")
        
        for i, user in enumerate(users):
            # A. 검색용 쿼리 (순수 제품 특징)
            concerns = ", ".join(user.get('concerns', []))
            skin = user.get('skin_type', '모든')
            search_query = f"{skin} 피부, {concerns} 해결 제품"
            
            # B. 생성용 컨텍스트 (전략 포함)
            strategy = ""
            if "모드 3" in mode: strategy = f"현재 날씨({weather_info}), 주간예보({weekly_weather})를 반영해 날씨에 맞는 멘트 작성"
            elif "모드 1" in mode: strategy = "고객의 피부 고민 공감과 맞춤 혜택 강조"
            
            # 실행
            product = search_best_product(search_query)
            if product:
                ctx = f"고객: {user['name']}({skin}), 고민: {concerns}, 전략: {strategy}"
                copy = generate_marketing_copy(product, ctx)
                st.session_state['messages'][i] = {"p": product['name'], "c": copy}
                st.session_state[f"edit_{i}"] = copy # 텍스트박스 갱신용
            else:
                st.session_state['messages'][i] = {"p": "추천 실패", "c": "적합한 제품을 찾지 못했습니다."}
            
            bar.progress((i+1)/10)
        bar.empty()
        st.toast("생성 완료!", icon="✅")

    st.write("---")
    for i, user in enumerate(get_users()[:10]):
        msg = st.session_state['messages'].get(i, {"p": "-", "c": ""})
        c1, c2 = st.columns([2, 1])
        with c1: st.markdown(f"**{user['name']}**")
        with c2: st.caption(f"📦 {msg['p']}")
        
        # 수정 가능한 텍스트 영역
        new_text = st.text_area("메시지 내용", value=msg['c'], key=f"edit_{i}", height=100, label_visibility="collapsed")
        if new_text != msg['c']:
            st.session_state['messages'][i]['c'] = new_text
        st.write("")

# 3. 오른쪽: 검색
with right:
    st.subheader("🔍 제품 검색")
    q = st.text_input("제품명/성분", placeholder="검색어 입력")
    if q:
        res = search_best_product(q)
        if res:
            with st.container(border=True):
                st.markdown(f"**{res['name']}**")
                st.caption(f"{res['price']}원")
                st.write(res['description'])
        else: st.warning("결과 없음")

st.divider()
st.subheader("📨 캠페인 발송")

col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    # 안전장치: 체크해야만 전송 가능
    confirm_send = st.checkbox("✅ 메시지 검토를 완료했으며, 실제 발송에 동의합니다.")

with col_s2:
    if st.button("🚀 실제 전송 시작", type="primary", disabled=not confirm_send, use_container_width=True):
        
        # 진행률 바
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 성공/실패 카운트
        success_count = 0
        fail_count = 0
        
        users = get_users()[:10] # 10명 대상
        
        for i, user in enumerate(users):
            # 생성된 메시지 가져오기 (없으면 기본값)
            msg_content = st.session_state.get('messages', {}).get(i, {}).get('copy', '')
            
            if msg_content:
                status_text.text(f"📤 {user['name']}님에게 메일 전송 중...")
                
                # [실제 전송] 이메일이 없으면 더미 이메일 사용
                target_email = user.get('email', 'dlwlssud123@naver.com') # 테스트용 본인 메일로 고정 추천
                subject = f"🎁 {user['name']}님을 위한 맞춤 뷰티 솔루션이 도착했어요!"
                
                is_sent, log = send_email(target_email, subject, msg_content)
                
                if is_sent: success_count += 1
                else: fail_count += 1
            
            time.sleep(0.5) # 너무 빠르면 스팸 차단될 수 있음
            progress_bar.progress((i + 1) / 10)
            
        progress_bar.empty()
        status_text.empty()
        
        # 결과 리포트
        if fail_count == 0:
            st.success(f"🎉 총 {success_count}명에게 성공적으로 발송되었습니다!")
            st.balloons()
        else:
            st.warning(f"⚠️ 발송 완료: 성공 {success_count}건, 실패 {fail_count}건")