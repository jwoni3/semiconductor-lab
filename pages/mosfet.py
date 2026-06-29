import streamlit as st
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="MOSFET AI 시뮬레이터", layout="wide", initial_sidebar_state="expanded")

# UI 최적화 CSS (AI 창 크기 조절 기능 추가)
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 98%; }
        .header-text { font-size: 20px; font-weight: 700; margin-bottom: 10px; margin-top: 5px; }
        
        /* 사이드바 배경 및 여백 최적화 (스크롤 방지) */
        [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
        [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        
        /* 슬라이더 간격 및 텍스트 박스 간격 대폭 축소 */
        .stSlider { padding-bottom: 0px !important; margin-bottom: -15px !important; }
        .stTextArea { padding-bottom: 0px !important; margin-bottom: -5px !important; }
        hr { margin-top: 10px !important; margin-bottom: 10px !important; }

        /* 우측 AI 컨테이너를 독립된 창처럼 만들고 '크기 조절(resize)' 기능 활성화 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #f1f5f9;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            padding: 10px;
            resize: both; /* 마우스 드래그로 가로/세로 크기 조절 허용 */
            overflow: auto; /* 내용이 넘치면 스크롤 생성 */
            min-height: 300px;
            min-width: 250px;
        }
        
        /* 다크모드 시 AI 창 색상 자동 반전 */
        @media (prefers-color-scheme: dark) {
            [data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #1e293b;
                border: 1px solid #334155;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>🔌 MOSFET 물리 시뮬레이터</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 좌측 사이드바: 제어 및 입력 패널
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### **🎛️ 제어 및 입력 패널**")
    
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    mos_type = st.selectbox("소자 타입 선택", ["NMOS", "PMOS"])
    
    # [수정] 피드백 반영: 입력 변수 배치 순서를 [문턱전압 -> 게이트전압 -> 드레인전압] 순으로 정렬
    if mos_type == "NMOS":
        v_th = st.slider("문턱 전압 (V_TH) [V]", 0.5, 2.0, 1.0, 0.1)
        v_gs = st.slider("게이트 전압 (V_GS) [V]", 0.0, 5.0, 3.0, 0.1)
        v_ds = st.slider("드레인 전압 (V_DS) [V]", 0.0, 5.0, 1.6, 0.1)
    else:
        v_th = st.slider("문턱 전압 (V_TH) [V]", -2.0, -0.5, -1.0, 0.1)
        v_gs = st.slider("게이트 전압 (V_GS) [V]", -5.0, 0.0, -3.0, 0.1)
        v_ds = st.slider("드레인 전압 (V_DS) [V]", -5.0, 0.0, -1.6, 0.1)

    st.markdown("---")
    
    user_query = st.text_area("질문 입력 구역", "현재 전압 상태를 물리적으로 설명해줘.", height=60, label_visibility="collapsed")
    ask_ai_btn = st.button("AI 실시간 해설 받기", type="primary", use_container_width=True)

# ---------------------------------------------------------
# 3. 물리 계산 로직 (수식 오류 전면 교정 및 그래프 동기화)
# ---------------------------------------------------------
k_n = 1.0
lambda_mod = 0.02  # 채널 길이 변조 계수

abs_vgs = abs(v_gs)
abs_vds = abs(v_ds)
abs_vth = abs(v_th)
v_ov = abs_vgs - abs_vth

# [수정] 수식 전면 수정: 그래프 그리기 알고리즘과 내부 계산용 연산식을 완벽하게 동기화시킴
if abs_vgs < abs_vth:
    op_region, i_d = "차단 영역 (Cutoff)", 0.0
elif abs_vds < v_ov:
    op_region, i_d = "선형 영역 (Linear)", k_n * (v_ov * abs_vds - 0.5 * (abs_vds ** 2))
else:
    op_region, i_d = "포화 영역 (Saturation)", 0.5 * k_n * (v_ov ** 2) * (1 + lambda_mod * (abs_vds - v_ov))

# ---------------------------------------------------------
# 4. 메인 대시보드 (3단 구성)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 1.2, 1.2], gap="medium")

# --- [Column 1] 소자 상태 및 구조 ---
with col1:
    st.markdown("<div class='header-text'>📊 실시간 소자 상태</div>", unsafe_allow_html=True)
    
    box_color = "#e6f7ff" if "포화" in op_region else "#f6ffed" if "선형" in op_region else "#fff1f0"
    st.markdown(f"""
    <div style='background-color:{box_color}; padding:10px; border-radius:8px; border:1px solid #ddd; text-align:center;'>
        <div style='font-size:12px; color:#475569; margin-bottom:2px;'>현재 동작 영역</div>
        <span style='font-size:18px; font-weight:700; color:#1e293b;'>{op_region}</span>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    m1.metric("인가 전압 (|V_DS|)", f"{abs_vds:.2f} V")
    m2.metric("드레인 전류 (|I_D|)", f"{i_d:.3f} mA")  # 정밀한 전류 비교 확인을 위해 소수점 3자리 확장
    
    st.markdown("<div class='header-text'>🧱 MOSFET 구조 시각화</div>", unsafe_allow_html=True)
    
    fig_struct = go.Figure()
    
    if mos_type == "NMOS":
        sub_color, sd_color, ch_color = "#e0f2fe", "#4ade80", "#fc8181" 
        sub_text, sd_label = "p-Substrate", "n+"
        pinch_color = "#b91c1c"
        ch_border_color = "#991b1b" 
    else:
        sub_color, sd_color, ch_color = "#ffe4e6", "#60a5fa", "#a855f7" 
        sub_text, sd_label = "n-Substrate", "p+"
        pinch_color = "#1d4ed8"
        ch_border_color = "#6b21a8" 

    fig_struct.add_shape(type="rect", x0=0, y0=0, x1=10, y1=4, fillcolor=sub_color, line=dict(width=0))
    fig_struct.add_shape(type="rect", x0=3, y0=4, x1=7, y1=4.15, fillcolor="#cbd5e1", line=dict(width=0))
    fig_struct.add_shape(type="rect", x0=3, y0=4.15, x1=7, y1=5.0, fillcolor="#1e293b", line=dict(width=0))
    
    fig_struct.add_shape(type="rect", x0=1, y0=2.5, x1=3, y1=4, fillcolor=sd_color, line=dict(width=0))
    fig_struct.add_shape(type="rect", x0=7, y0=2.5, x1=9, y1=4, fillcolor=sd_color, line=dict(width=0))
    
    fig_struct.add_shape(type="line", x0=0.5, y0=2.0, x1=9.5, y1=2.0, line=dict(color="#94a3b8", width=1.5, dash="dot"))
    fig_struct.add_annotation(x=5, y=1.6, text="<i>Depletion Region</i>", font=dict(color="#64748b", size=11), showarrow=False)

    if op_region != "차단 영역 (Cutoff)":
        if op_region == "선형 영역 (Linear)":
            t_d = 4.0 - 0.2 * (1 - abs_vds / max(v_ov, 0.001))
            fig_struct.add_shape(type="path", path=f"M 3 4 L 7 4 L 7 {t_d} L 3 3.85 Z", fillcolor=ch_color, line=dict(color=ch_border_color, width=2), opacity=0.85)
        else:
            p_p = max(4.0, 7 - (abs_vds - v_ov) * 0.8)
            fig_struct.add_shape(type="path", path=f"M 3 4 L {p_p} 4 L 3 3.85 Z", fillcolor=ch_color, line=dict(color=ch_border_color, width=2), opacity=0.85)
            fig_struct.add_shape(type="line", x0=p_p, y0=0, x1=p_p, y1=5.5, line=dict(color=pinch_color, width=2, dash="dash"))
            fig_struct.add_annotation(x=p_p, y=5.7, text="Pinch-off", font=dict(color=pinch_color, size=10), showarrow=False)

    fig_struct.add_annotation(x=2, y=3.5, text="<b>S</b>", font=dict(color="white", size=20), showarrow=False)
    fig_struct.add_annotation(x=2, y=3.0, text=f"<i>{sd_label}</i>", font=dict(color="white", size=14), showarrow=False)
    fig_struct.add_annotation(x=8, y=3.5, text="<b>D</b>", font=dict(color="white", size=20), showarrow=False)
    fig_struct.add_annotation(x=8, y=3.0, text=f"<i>{sd_label}</i>", font=dict(color="white", size=14), showarrow=False)
    fig_struct.add_annotation(x=5, y=4.55, text="Gate (G)", font=dict(color="white", size=12), showarrow=False)
    fig_struct.add_annotation(x=5, y=0.5, text=sub_text, font=dict(color="#475569", size=13), showarrow=False)

    fig_struct.update_layout(height=230, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(visible=False, range=[0, 10]), yaxis=dict(visible=False, range=[0, 6]), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_struct, use_container_width=True, theme="streamlit")

# --- [Column 2] I-V 특성 곡선 ---
with col2:
    st.markdown("<div class='header-text'>📈 전류-전압 특성 곡선</div>", unsafe_allow_html=True)
    
    v_ax = np.linspace(0, 5, 200)
    v_b = np.linspace(0, 5, 200) # 포화 경계선 도메인 일치
    
    # 포화 상태 경계선 수식 매핑 및 동기화 조치
    i_b = 0.5 * k_n * (v_b**2)

    fig_iv = go.Figure()
    fig_iv.add_trace(go.Scatter(x=v_b, y=i_b, mode='lines', line=dict(color='#cbd5e1', dash='dash', width=1.5), name="포화 영역 경계선"))
    
    # [수정] 수식 동기화: 동적 변경되는 연산식 루프의 계산법을 상단 calc 필드와 완벽하게 한 방향으로 수정
    i_ax = []
    for v in v_ax:
        if abs_vgs < abs_vth:
            i_ax.append(0.0)
        elif v < v_ov:
            i_ax.append(k_n * (v_ov * v - 0.5 * (v ** 2)))
        else:
            i_ax.append(0.5 * k_n * (v_ov ** 2) * (1 + lambda_mod * (v - v_ov)))

    fig_iv.add_trace(go.Scatter(x=v_ax, y=i_ax, mode='lines', line=dict(color='#3b82f6', width=3), name="I-V 특성 곡선"))
    fig_iv.add_trace(go.Scatter(x=[abs_vds], y=[i_d], mode='markers', marker=dict(color='#ef4444', size=12, line=dict(color='white', width=1.5)), name="현재 동작점"))
    
    fig_iv.update_layout(
        height=350, 
        margin=dict(l=0, r=0, t=10, b=0), 
        xaxis_title="V_DS (V)", 
        yaxis_title="I_D (mA)", 
        showlegend=True, 
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(128, 128, 128, 0.1)", bordercolor="rgba(128,128,128,0.2)", borderwidth=1),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_iv.update_xaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', range=[0, 5])
    fig_iv.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', range=[0, max(max(i_ax)*1.1, 2.0)])
    st.plotly_chart(fig_iv, use_container_width=True, theme="streamlit")

# --- [Column 3] AI 실시간 해설 (크기 조절 가능) ---
with col3:
    with st.container(border=True):
        st.markdown("<div class='header-text' style='text-align: center; color: #3b82f6;'>🤖 AI 실시간 해설</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        if ask_ai_btn:
            if not api_key:
                st.error("⚠️ 좌측 사이드바에 API Key를 입력해주세요.")
            else:
                with st.spinner("반도체 물성 분석 중..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        
                        prompt = f"""
                        너는 학부 및 대학원 수준의 반도체 공학 전문가야. 아래 정보를 바탕으로 현재 MOSFET의 상태를 물리적으로 깊이 있게 분석해줘.
                        
                        [상태 정보]
                        - 소자: {mos_type}
                        - V_GS={v_gs}V, V_DS={v_ds}V, V_TH={v_th}V
                        - 동작 영역: {op_region}
                        - I_D={i_d:.3f}mA
                        
                        [사용자 질문]
                        {
