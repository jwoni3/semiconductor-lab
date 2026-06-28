import streamlit as st

st.set_page_config(
    page_title="Semiconductor Device Simulator",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Noto Sans KR', sans-serif; }

    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 6px;
    }
    .hero-sub {
        font-size: 16px;
        color: #666;
        text-align: center;
        margin-bottom: 36px;
    }
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px 24px 16px 24px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 2px solid transparent;
        margin-bottom: 0px;
    }
    .card-icon { font-size: 40px; margin-bottom: 10px; }
    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 8px;
    }
    .card-desc {
        font-size: 12px;
        color: #777;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 4px;
    }
    .badge-ready { background: #e8f5e9; color: #2e7d32; }
    .badge-soon  { background: #fff3e0; color: #e65100; }

    [data-testid="stPageLink"] a {
        font-size: 16px !important;
        font-weight: 700 !important;
        padding: 14px 0px !important;
        border-radius: 12px !important;
        background-color: #1a1a2e !important;
        color: white !important;
        display: block;
        text-align: center;
    }
    [data-testid="stPageLink"] a p {
        color: white !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    [data-testid="stPageLink"] a:hover {
        background-color: #2e2e5e !important;
    }

    .divider {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 48px auto;
        width: 60%;
    }
    .footer {
        text-align: center;
        font-size: 12px;
        color: #aaa;
        margin-top: 24px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='hero-title'>⚡ Semiconductor Device Simulator</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>시뮬레이션할 반도체 소자를 선택하세요</div>", unsafe_allow_html=True)

col1, col_gap, col2 = st.columns([1, 0.15, 1])

with col1:
    st.markdown("""
    <div class='card'>
        <div class='card-icon'>🔌</div>
        <div class='card-title'>MOSFET 시뮬레이터</div>
        <div class='card-desc'>
            NMOS / PMOS 소자의 I-V 특성 곡선,<br>
            에너지 밴드 다이어그램, 채널 구조를<br>
            실시간으로 시각화합니다.
        </div>
        <span class='badge badge-ready'>✅ 사용 가능</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/mosfet.py", label="🔌 MOSFET 시뮬레이터 시작", use_container_width=True)

with col2:
    st.markdown("""
    <div class='card'>
        <div class='card-icon'>🔬</div>
        <div class='card-title'>BJT 시뮬레이터</div>
        <div class='card-desc'>
            NPN / PNP 바이폴라 트랜지스터의<br>
            동작 영역 분석과 전류 이득 특성을<br>
            시각화합니다.
        </div>
        <span class='badge badge-soon'>🚧 준비 중</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/bjt.py", label="🔬 BJT 시뮬레이터 시작", use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='footer'>Semiconductor Device Simulator · Powered by Streamlit & Gemini AI</div>",
            unsafe_allow_html=True)
