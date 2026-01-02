import streamlit as st
import os
import json
import time
import pandas as pd
import requests
import altair as alt
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

# --- 로컬 모듈 임포트 ---
from vector_db import init_db, search_best_product, search_products
from generator import generate_marketing_copy
from sender import send_email

# --- [초기 설정] ---
load_dotenv()
st.set_page_config(page_title="Glow Code AI", page_icon="✨", layout="wide")

# CSS 커스텀 스타일링
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .weather-badge {
        background-color: #f0f8ff;
        color: #007bff;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
    }
    div[data-testid="stExpander"] {
        background-color: #f9f9f9;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# DB 초기화
if 'db_initialized' not in st.session_state:
    with st.spinner("🚀 시스템 리소스를 불러오는 중..."):
        init_db(force_reset=True)
        st.session_state['db_initialized'] = True

if 'messages' not in st.session_state:
    st.session_state['messages'] = {}

# --- [유틸리티 함수] ---
def get_users():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def load_history():
    """발송 이력 불러오기"""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history.csv')
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_history(log_data):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history.csv')
    df_new = pd.DataFrame(log_data)
    if not os.path.exists(path):
        df_new.to_csv(path, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(path, mode='a', header=False, index=False, encoding='utf-8-sig')

def get_weather(city="Daegu"):
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key: return "📍 대구 | ☀️ 24°C (API키 미설정)"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric&lang=kr"
        data = requests.get(url).json()
        return f"📍 {city} | 🌡️ {int(data['main']['temp'])}°C {data['weather'][0]['description']}"
    except: return f"📍 {city} | ☀️ 날씨 정보 수신 불가"

# --- [사이드바] ---
with st.sidebar:
    st.title("✨ Glow Code")
    st.caption("AI-Powered CRM Solution")
    
    st.markdown("### ⛅ 현재 날씨")
    weather_info = get_weather("Daegu")
    st.markdown(f'<div class="weather-badge">{weather_info}</div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 👤 사용자 프로필")
    users = get_users()
    st.info(f"등록 고객: {len(users)}명")
    
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.session_state['messages'] = {}
        st.rerun()

# --- [메인 레이아웃: 탭 구조] ---
tab1, tab2, tab3 = st.tabs(["📊 통합 대시보드", "💌 CRM 캠페인 실행", "🔍 제품 검색"])

# -----------------------------------------------------------------------------
# [TAB 1] 통합 대시보드 (분석 리포트 강화)
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("📈 고객 및 캠페인 현황")
    
    # 1. 핵심 지표 (KPI Cards)
    users = get_users()
    history_df = load_history()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 고객 수", f"{len(users)}명", "+2명")
    with col2:
        total_sent = len(history_df) if not history_df.empty else 0
        st.metric("누적 발송 건수", f"{total_sent}건", "Today +5")
    with col3:
        # 가상의 데이터 (데모용)
        st.metric("평균 메시지 매칭률", "94.5%", "+1.2%")
    with col4:
        st.metric("예상 전환 매출", "₩2,450,000", "+5%")
        
    st.markdown("---")
    
    # 2. 상세 분석 차트
    chart_col1, chart_col2 = st.columns(2)
    
    if users:
        df_users = pd.DataFrame(users)
        
        # [차트 1] 피부 타입 분포
        with chart_col1:
            st.markdown("#### 🧴 고객 피부 타입 분포")
            type_counts = df_users['skin_type'].value_counts().reset_index()
            type_counts.columns = ['type', 'count']
            
            c = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="count", type="quantitative"),
                color=alt.Color(field="type", type="nominal", legend=None),
                tooltip=['type', 'count']
            ).properties(height=250)
            st.altair_chart(c, use_container_width=True)

        # [차트 2] 주요 고민 키워드
        with chart_col2:
            st.markdown("#### 🆘 주요 피부 고민 Top 5")
            all_concerns = [c for sublist in df_users['concerns'] for c in sublist]
            concern_counts = pd.DataFrame(Counter(all_concerns).most_common(5), columns=['keyword', 'count'])
            
            bar = alt.Chart(concern_counts).mark_bar().encode(
                x='count:Q',
                y=alt.Y('keyword:N', sort='-x'),
                color=alt.value('#ff9aa2')
            ).properties(height=250)
            st.altair_chart(bar, use_container_width=True)

    # 3. 최근 활동 로그
    st.markdown("#### 🕒 최근 발송 이력")
    if not history_df.empty:
        st.dataframe(
            history_df.tail(5)[['timestamp', 'user', 'product', 'status']].sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("아직 발송 이력이 없습니다.")


# -----------------------------------------------------------------------------
# [TAB 2] CRM 캠페인 실행 (메시지 생성 UI 개선)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("✉️ 개인화 메시지 생성기")
    
    # 1. 설정 섹션 (Expander로 깔끔하게)
    with st.expander("🛠️ 캠페인 전략 설정", expanded=True):
        col_opt1, col_opt2 = st.columns([2, 1])
        with col_opt1:
            mode = st.radio(
                "AI 페르소나 모드", 
                ["모드 1: 감성/공감형 (피부 고민 위주)", "모드 2: 전문가/분석형 (성분 위주)", "모드 3: 트렌드/시즌형 (날씨 위주)"],
                horizontal=True
            )
        with col_opt2:
            target_count = st.slider("생성 대상 인원", 1, 10, 5)
    
    # 2. 실행 버튼
    if st.button("🚀 AI 메시지 생성 시작", type="primary", use_container_width=True):
        st.session_state['messages'] = {} # 초기화
        
        # 상태 표시창 (깔끔한 로딩)
        with st.status("🤖 AI가 고객 정보를 분석하고 메시지를 작성 중입니다...", expanded=True) as status:
            target_users = get_users()[:target_count]
            progress_bar = st.progress(0)
            
            for i, user in enumerate(target_users):
                # 1) 검색
                concerns = ", ".join(user.get('concerns', []))
                query = f"{user.get('skin_type', '')} 피부, {concerns} 해결"
                
                # 2) 전략 주입
                strategy_ctx = ""
                if "모드 3" in mode: 
                    query += f", (날씨: {weather_info})"
                    strategy_ctx = f"(상황: 현재 날씨 {weather_info} 반영)"
                elif "모드 1" in mode: strategy_ctx = "(전략: 공감과 위로)"
                elif "모드 2" in mode: strategy_ctx = "(전략: 전문적인 성분 분석)"
                
                status.write(f"🔍 {user['name']}님 분석 중... ({query})")
                
                best_product = search_best_product(query)
                
                if best_product:
                    context = f"고객: {user['name']}({user.get('skin_type')}), 고민: {concerns}, {strategy_ctx}"
                    copy = generate_marketing_copy(best_product, context)
                    
                    st.session_state['messages'][i] = {
                        "user": user,
                        "product": best_product['name'],
                        "brand": best_product.get('brand', 'Unknown'),
                        "copy": copy,
                        "score": 90 + (i % 8) # 모의 점수
                    }
                time.sleep(0.3) # 시각적 효과
                progress_bar.progress((i+1)/len(target_users))
            
            status.update(label="✅ 생성이 완료되었습니다!", state="complete", expanded=False)

    # 3. 결과 표시 (그리드 레이아웃 적용)
    if st.session_state['messages']:
        st.divider()
        st.markdown(f"#### 📋 생성 결과 ({len(st.session_state['messages'])}건)")
        
        # 2열 그리드로 표시
        cols = st.columns(2)
        
        for i, (idx, msg_data) in enumerate(st.session_state['messages'].items()):
            with cols[i % 2]: # 지그재그 배치
                with st.container(border=True):
                    # 헤더: 이름 + 매칭점수
                    h1, h2 = st.columns([3, 1])
                    with h1: st.markdown(f"**👤 {msg_data['user']['name']}**님")
                    with h2: st.markdown(f"🔥 `{msg_data['score']}%`")
                    
                    # 상품 정보
                    st.caption(f"🎁 추천 제품: **[{msg_data['brand']}] {msg_data['product']}**")
                    
                    # 편집 가능한 메시지
                    new_copy = st.text_area(
                        "메시지 내용",
                        value=msg_data['copy'],
                        height=120,
                        key=f"edit_{idx}",
                        label_visibility="collapsed"
                    )
                    # 수정 사항 반영
                    if new_copy != msg_data['copy']:
                        st.session_state['messages'][idx]['copy'] = new_copy

        # 4. 일괄 전송 액션
        st.markdown("---")
        c1, c2 = st.columns([3, 1])
        with c1:
            agree = st.checkbox("✅ 메시지 내용을 모두 확인했으며, 실제 발송에 동의합니다.")
        with c2:
            if st.button("📨 일괄 전송 및 저장", type="primary", disabled=not agree, use_container_width=True):
                success_count = 0
                send_status = st.status("📤 메일을 전송하고 있습니다...")
                logs = []
                
                for idx, msg_data in st.session_state['messages'].items():
                    user = msg_data['user']
                    target_email = user.get('email')
                    
                    # 실제 전송
                    is_sent, _ = send_email(target_email, f"[GlowCode] {user['name']}님을 위한 추천", msg_data['copy'])
                    
                    # 로그 생성
                    logs.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user": user['name'],
                        "product": msg_data['product'],
                        "status": "성공" if is_sent else "실패"
                    })
                    if is_sent: success_count += 1
                
                # 저장
                save_history(logs)
                send_status.update(label=f"🎉 {success_count}건 전송 완료!", state="complete")
                st.balloons()


# -----------------------------------------------------------------------------
# [TAB 3] 제품 검색 (심플하고 넓게)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🔍 아모레몰 제품 데이터베이스")
    
    col_search, col_dum = st.columns([2, 1])
    with col_search:
        search_q = st.text_input("제품명, 성분, 효능으로 검색해보세요", placeholder="예: 레티놀, 시카, 탄력 크림")
    
    if search_q and len(search_q.strip()) >= 2:
        # vector_db.py의 search_products 사용
        results = search_products(search_q, limit=10)
        
        if results:
            st.success(f"🔎 검색 결과 {len(results)}건")
            
            for item in results:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**[{item.get('brand','Brand')}] {item.get('name')}**")
                        st.caption(item.get('description'))
                    with c2:
                        st.markdown(f"**{item.get('price','-')}원**")
                        st.caption(f"추천: {item.get('skin_type')}")
        else:
            st.warning("검색 결과가 없습니다.")