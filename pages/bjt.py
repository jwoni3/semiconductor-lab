import streamlit as st

st.set_page_config(
    page_title="BJT Simulator",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Noto Sans KR', sans-serif; }
    .center {
        text-align: center;
        margin-top: 80px;
    }
    .icon { font-size: 72px; margin-bottom: 24px; }
    .title {
        font-size: 32px;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 12px;
    }
    .desc {
        font-size: 15px;
        color: #777;
        line-height: 1.8;
        margin-bottom: 36px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='center'>
    <div class='icon'>🚧</div>
    <div class='title'>BJT 시뮬레이터 준비 중</div>
    <div class='desc'>
        NPN / PNP 바이폴라 트랜지스터 시뮬레이터를 개발 중입니다.<br>
        곧 업데이트될 예정이니 조금만 기다려 주세요!
    </div>
</div>
""", unsafe_allow_html=True)

st.page_link("app.py", label="← 홈으로 돌아가기", use_container_width=False)