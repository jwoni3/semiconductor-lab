import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
import plotly.graph_objects as go
import requests

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="MOSFET SIMULATOR",
    page_icon="🔌",
    layout="wide"
)

# ── CSS 스타일 (사이드바 컴팩트화 스타일 추가) ─────────────────
st.markdown("""
<style>
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2a2a4e !important;
        border-color: #555 !important;
        color: white !important;
    }     
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="stSidebar"] div.stButton > button {
        background-color: #2a2a4e !important;   /* 셀렉트박스와 톤 일치 */
        color: white !important;                 /* 글자색 흰색으로 선명하게 */
        border: 1px solid #555 !important;      /* 셀렉트박스와 동일한 테두리 */
        border-radius: 8px !important;
        transition: background-color 0.2s ease;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #3b3b6d !important;   /* 마우스 올렸을 때 자연스럽게 밝아짐 */
        border-color: #777 !important;
    }

    /* 사이드바 내부 요소 간 간격 극대화 축소 (컴팩트 스크롤 방지용) */
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        margin-bottom: -5px !important;
    }
    [data-testid="stSidebar"] .stSlider {
        margin-top: -10px !important;
        padding-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Gemini REST API ───────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

def call_gemini(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP 오류: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"❌ API 통신 오류: {e}"

# ── 세션 상태 초기화 ─────────────────────────────────────────
for key, default in [("vth_val", 1.0), ("vgs_val", 2.6), ("vds_val", 3.7)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── 사이드바 (Compact Layout 적용) ───────────────────────────
with st.sidebar:
    # 🏠 홈으로 돌아가기 버튼
    if st.button("⬅ 홈으로 돌아가기", use_container_width=True):
        st.switch_page("app.py") 
        
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎛️ 제어 및 입력 패널")

    device = st.selectbox("소자 타입 선택", ["NMOS", "PMOS"])
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    # 슬라이더 컴팩트 배치 적용
    st.markdown("**문턱 전압 |V_TH| (V)**")
    st.markdown("<div style='height: 7px;'></div>", unsafe_allow_html=True)
    vth = st.slider("V_TH", 0.0, 2.0,
                    value=float(st.session_state["vth_val"]),
                    step=0.1, key="vth_slide",
                    label_visibility="collapsed")
    st.session_state["vth_val"] = vth

    st.markdown("**게이트 전압 V_GS (V)**")
    st.markdown("<div style='height: 7px;'></div>", unsafe_allow_html=True)
    vgs = st.slider("V_GS", 0.0, 5.0,
                    value=float(st.session_state["vgs_val"]),
                    step=0.1, key="vgs_slide",
                    label_visibility="collapsed")
    st.session_state["vgs_val"] = vgs

    st.markdown("**드레인 전압 V_DS (V)**")
    st.markdown("<div style='height: 7px;'></div>", unsafe_allow_html=True)
    vds = st.slider("V_DS", 0.0, 5.0,
                    value=float(st.session_state["vds_val"]),
                    step=0.1, key="vds_slide",
                    label_visibility="collapsed")
    st.session_state["vds_val"] = vds

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    st.markdown("**🤖 ASK AI**")
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    user_question = st.text_area(
        "", height=65,  # 한눈에 보이도록 높이 축소
        placeholder="e.g. 현재 전압 조건 상태에 대해 물리적으로 쉽게 설명해줘.",
        label_visibility="collapsed"
    )
    ask_btn = st.button("☉ AI 실시간 해설 보기", use_container_width=True, type="primary")


# ── MOSFET 물리 계산 ─────────────────────────────────────────
def calc_mosfet(device, vgs, vds, vth, Kn=1.0, Kp=1.0):
    if device == "NMOS":
        vgs_eff = vgs - vth
        vds_sat = max(vgs_eff, 0.0)
        if vgs_eff <= 0:
            region = "Cutoff";  id_mA = 0.0
        elif vds < vgs_eff:
            region = "Linear"
            id_mA = round(Kn * (vgs_eff * vds - 0.5 * vds**2), 2)
        else:
            region = "Saturation"
            id_mA = round(0.5 * Kn * vgs_eff**2, 2)
    else:
        vgs_real = -vgs; vds_real = -vds; vth_real = -vth
        vgs_eff  = vth_real - vgs_real
        vds_sat  = max(vgs_eff, 0.0)
        if vgs_real > vth_real:
            region = "Cutoff";  id_mA = 0.0
        elif abs(vds_real) < vgs_eff:
            region = "Linear"
            id_mA = round(Kp * (vgs_eff * abs(vds_real) - 0.5 * abs(vds_real)**2), 2)
        else:
            region = "Saturation"
            id_mA = round(0.5 * Kp * vgs_eff**2, 2)
    return region, id_mA, vds_sat

region, id_mA, vds_sat = calc_mosfet(device, vgs, vds, vth)

region_kr = {
    "Cutoff":     "차단 영역 (Cutoff)",
    "Linear":     "선형 영역 (Linear)",
    "Saturation": "포화 영역 (Saturation)"
}.get(region, region)

# ── 타이틀 ───────────────────────────────────────────────────
st.markdown(f"# 🔌 {device} MOSFET SIMULATOR")
st.divider()

col_left, col_mid, col_right = st.columns([1, 1.4, 1])

# ════════════════════════════════════════════════════════════
# 1열: 소자 상태 + 구조 시각화
# ════════════════════════════════════════════════════════════
with col_left:
    st.markdown("### 📊 소자 상태")
    region_color = (
        "#28a745" if region == "Saturation" else
        "#ffc107" if region == "Linear" else
        "#dc3545"
    )
    st.markdown(f"""
    <div style='margin-bottom:8px'>
        <div style='font-size:13px;color:#666;margin-bottom:4px'>Operating Region</div>
        <div style='font-size:26px;font-weight:700;color:{region_color}'>{region_kr}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style='padding:8px 0'>
            <div style='font-size:11px;color:#666;margin-bottom:2px'>인가전압 |V_DS|</div>
            <div style='font-size:28px;font-weight:700;color:#1a1a2e'>{vds:.2f} V</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='padding:8px 0'>
            <div style='font-size:11px;color:#666;margin-bottom:2px'>드레인전류 |I_D|</div>
            <div style='font-size:28px;font-weight:700;color:#1a1a2e'>{id_mA:.2f} mA</div>
        </div>""", unsafe_allow_html=True)
    st.container().markdown("")

    # ── MOSFET 구조 시각화 ───────────────────────────────
    st.markdown("### 📐 MOSFET 구조")
    fig_struct, ax = plt.subplots(figsize=(5, 4.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8.5); ax.axis("off")
    fig_struct.patch.set_facecolor('white')

    sub_color     = "#c8dff0" if device == "NMOS" else "#fce4d6"
    sub_edge      = "#5a8abf" if device == "NMOS" else "#e67e22"
    sub_text      = "p-Substrate" if device == "NMOS" else "n-Substrate"
    sub_tc        = "#2c5f8a" if device == "NMOS" else "#a04000"
    well_text     = "n+" if device == "NMOS" else "p+"
    well_color    = "#4caf7d" if device == "NMOS" else "#9b59b6"
    well_edge     = "#2e7d52" if device == "NMOS" else "#8e44ad"
    carrier_color = "#e65100" if device == "NMOS" else "#8e44ad"
    ch_color      = "#66bb6a" if device == "NMOS" else "#d2b4de"
    ch_edge       = "#388e3c" if device == "NMOS" else "#af7ac5"

    ax.add_patch(patches.FancyBboxPatch(
        (0.3, 0.3), 9.4, 4.8, boxstyle="round,pad=0.1",
        fc=sub_color, ec=sub_edge, lw=1.5))
    ax.text(5, 1.0, sub_text, ha="center", va="center",
            fontsize=10, color=sub_tc, fontstyle='italic')

    for (x0, label) in [(0.5, "S"), (7.2, "D")]:
        ax.add_patch(patches.FancyBboxPatch(
            (x0, 3.0), 2.3, 2.1, boxstyle="round,pad=0.05",
            fc=well_color, ec=well_edge, lw=1.5))
        cx = x0 + 1.15
        ax.text(cx, 4.1, label, ha="center", va="center",
                fontsize=18, fontweight="bold", color="white")
        ax.text(cx, 3.35, well_text, ha="center", va="center",
                fontsize=10, color="#ffffff")

    ax.add_patch(patches.Rectangle(
        (2.8, 5.1), 4.4, 0.4, fc="#e8e8e8", ec="#aaa", lw=1.0))
    ax.text(7.35, 5.3, "SiO2", ha="left", va="center", fontsize=8, color="#9400D3")

    ax.add_patch(patches.FancyBboxPatch(
        (2.8, 5.5), 4.4, 0.75, boxstyle="round,pad=0.05",
        fc="#37474f", ec="#1a1a2e", lw=1.5))
    ax.text(5, 5.88, "Gate (G)", ha="center", va="center",
            fontsize=10, fontweight="bold", color="white")

    GATE_X_START, GATE_X_END = 2.8, 7.2
    GATE_LEN = GATE_X_END - GATE_X_START
    SIO2_BOTTOM, CH_THICK = 5.1, 0.5

    if region == "Saturation":
        ratio = float(np.clip(vds_sat / max(abs(vds), 0.01), 0.15, 0.85))
        po_x = (GATE_X_START + GATE_LEN * ratio if device == "NMOS"
                else GATE_X_END - GATE_LEN * ratio)
        if device == "NMOS":
            tri_pts  = np.array([[GATE_X_START, SIO2_BOTTOM],
                                  [po_x, SIO2_BOTTOM],
                                  [GATE_X_START, SIO2_BOTTOM - CH_THICK]])
            dep_rect = patches.Rectangle(
                (po_x, SIO2_BOTTOM - CH_THICK), GATE_X_END - po_x, CH_THICK,
                fc="#dce8f5", ec="#5a8abf", linestyle='--', alpha=0.6)
            arr_start, arr_end = GATE_X_START + 0.2, po_x - 0.15
        else:
            tri_pts  = np.array([[GATE_X_END, SIO2_BOTTOM],
                                  [po_x, SIO2_BOTTOM],
                                  [GATE_X_END, SIO2_BOTTOM - CH_THICK]])
            dep_rect = patches.Rectangle(
                (GATE_X_START, SIO2_BOTTOM - CH_THICK), po_x - GATE_X_START, CH_THICK,
                fc="#fbeee6", ec="#e67e22", linestyle='--', alpha=0.6)
            arr_start, arr_end = GATE_X_END - 0.2, po_x + 0.15

        ax.add_patch(MplPolygon(tri_pts, closed=True, fc=ch_color, ec=ch_edge,
                                lw=1.2, alpha=0.9, zorder=4))
        ax.add_patch(dep_rect)
        ax.plot(po_x, SIO2_BOTTOM, 'ro', ms=7, zorder=10)
        ax.text(po_x, SIO2_BOTTOM - 0.8, "Pinch-off",
                ha="center", fontsize=7, color="red", fontweight="bold")
        ax.annotate("", xy=(arr_end, SIO2_BOTTOM - CH_THICK * 0.4),
                    xytext=(arr_start, SIO2_BOTTOM - CH_THICK * 0.4),
                    arrowprops=dict(arrowstyle='->', color=carrier_color, lw=1.4), zorder=6)

    elif region == "Linear":
        drain_thin = CH_THICK * (1.0 - 0.4 * (vds / (vds_sat if vds_sat > 0 else 1)))
        trap_pts = np.array([[GATE_X_START, SIO2_BOTTOM],
                             [GATE_X_END,   SIO2_BOTTOM],
                             [GATE_X_END,   SIO2_BOTTOM - drain_thin],
                             [GATE_X_START, SIO2_BOTTOM - CH_THICK]])
        ax.add_patch(MplPolygon(trap_pts, closed=True, fc=ch_color, ec=ch_edge,
                                lw=1.2, alpha=0.85, zorder=4))
    else:
        ax.text(5, SIO2_BOTTOM - 0.35, "No Channel (Cutoff)",
                ha="center", va="top", fontsize=8, color="#dc3545",
                bbox=dict(boxstyle='round,pad=0.3', fc='#fff0f0', ec='#dc3545', alpha=0.85))

    ax.text(5, 7.8, f"Applied: V_GS={vgs:.1f}V | V_DS={vds:.1f}V",
            ha="center", fontsize=8, color="#444")
    st.pyplot(fig_struct)
    plt.close(fig_struct)


# ════════════════════════════════════════════════════════════
# 2열: I-V 곡선(plotly) + 에너지밴드(matplotlib)
# ════════════════════════════════════════════════════════════
with col_mid:
    st.markdown("### 📈 전류-전압 특성 곡선 & 에너지 밴드 다이어그램")

    # ── I-V 특성 곡선 (plotly) ───────────────────────────
    v_ax = np.linspace(0, 5, 300)
    i_ax = [calc_mosfet(device, vgs, vd, vth)[1] for vd in v_ax]

    vgs_for_boundary = np.linspace(vth + 0.01, 5.0, 300)
    sat_vds_pts, sat_id_pts = [], []
    for vg_ in vgs_for_boundary:
        vds_b = vg_ - vth
        id_b  = round(0.5 * (vg_ - vth) ** 2, 2)
        if 0 <= vds_b <= 5.0:
            sat_vds_pts.append(vds_b)
            sat_id_pts.append(id_b)

    fig_iv = go.Figure()
    fig_iv.add_trace(go.Scatter(
        x=sat_vds_pts, y=sat_id_pts, mode='lines',
        line=dict(color='#e74c3c', dash='dash', width=1.8),
        name="Saturation Boundary (V_DS = V_GS − V_TH)"
    ))
    fig_iv.add_trace(go.Scatter(
        x=list(v_ax), y=i_ax, mode='lines',
        line=dict(color='#1a5276', width=2.5),
        name=f"V_GS = {vgs:.1f} V"
    ))
    fig_iv.add_trace(go.Scatter(
        x=[vds], y=[id_mA], mode='markers',
        marker=dict(color='#e74c3c', size=11, line=dict(color='white', width=1.5)),
        name="Operating Point"
    ))
    fig_iv.update_layout(
        height=300, margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="|V_DS| (V)" if device == "PMOS" else "V_DS (V)",
        yaxis_title="I_D (mA)",
        xaxis=dict(range=[0, 5]), yaxis=dict(rangemode='tozero'),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01,
                    bgcolor="rgba(255,255,255,0.85)",
                    bordercolor="rgba(128,128,128,0.3)", borderwidth=1,
                    font=dict(size=9)),
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="I-V Characteristic Curve", font=dict(size=11),
                   x=0.5, xanchor='center')
    )
    fig_iv.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    fig_iv.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    st.plotly_chart(fig_iv, use_container_width=True, theme="streamlit")
    st.container().markdown("")

    # ── 에너지 밴드 다이어그램 (plotly, Source-Channel-Drain 3구간) ──
    Eg   = 1.12
    E0   = 2.0

    abs_vgs = abs(vgs)
    abs_vds = abs(vds)
    abs_vth = abs(vth)
    vgs_eff_plot = max(abs_vgs - abs_vth, 0.0)

    bend_sign = -1.0 if device == "NMOS" else +1.0
    bend_ch   = bend_sign * min(vgs_eff_plot, 2.5) * 0.55
    drop_d    = -min(abs_vds, 3.0) * 0.4

    x_src = np.linspace(0.0, 1.0, 50)
    x_ch  = np.linspace(1.0, 2.0, 80)
    x_drn = np.linspace(2.0, 3.0, 50)

    ec_src = np.full_like(x_src, E0)
    ec_ch  = np.linspace(E0, E0 + bend_ch, len(x_ch))
    ec_drn = np.linspace(E0 + bend_ch, E0 + bend_ch + drop_d, len(x_drn))

    ev_src = ec_src - Eg
    ev_ch  = ec_ch  - Eg
    ev_drn = ec_drn - Eg

    x_all  = np.concatenate([x_src, x_ch,  x_drn])
    ec_all = np.concatenate([ec_src, ec_ch, ec_drn])
    ev_all = np.concatenate([ev_src, ev_ch, ev_drn])

    ef_src_val = E0 - Eg / 2 + 0.1
    ef_drn_val = ef_src_val + drop_d

    fig_band = go.Figure()

    fig_band.add_trace(go.Scatter(
        x=list(x_all), y=list(ec_all), mode='lines',
        line=dict(color='#e74c3c', width=2.5),
        name="E<sub>c</sub>"
    ))
    fig_band.add_trace(go.Scatter(
        x=list(x_all), y=list(ev_all), mode='lines',
        line=dict(color='#2980b9', width=2.5),
        name="E<sub>v</sub>"
    ))
    fig_band.add_trace(go.Scatter(
        x=[0.0, 1.0], y=[ef_src_val, ef_src_val], mode='lines',
        line=dict(color='purple', width=1.5, dash='dot'),
        name="E<sub>f</sub>"
    ))
    fig_band.add_trace(go.Scatter(
        x=[2.0, 3.0], y=[ef_drn_val, ef_drn_val], mode='lines',
        line=dict(color='purple', width=1.5, dash='dot'),
        showlegend=False
    ))

    # Eg 양방향 화살표
    fig_band.add_annotation(
        x=0.15, y=ec_src[0], ay=ev_src[0],
        axref='x', ayref='y', xref='x', yref='y',
        arrowhead=2, arrowsize=1, arrowwidth=1.2,
        arrowcolor='gray', ax=0.15
    )
    fig_band.add_annotation(
        x=0.15, y=ev_src[0], ay=ec_src[0],
        axref='x', ayref='y', xref='x', yref='y',
        arrowhead=2, arrowsize=1, arrowwidth=1.2,
        arrowcolor='gray', ax=0.15
    )
    fig_band.add_annotation(
        x=0.2, y=(ec_src[0] + ev_src[0]) / 2,
        text=f"Eg={Eg}eV", showarrow=False,
        font=dict(size=9, color='gray'), xanchor='left'
    )

    # 동작 영역 레이블
    if region == "Saturation" and vgs_eff_plot > 0:
        fig_band.add_annotation(
            x=1.5, y=E0 + bend_ch - 0.15,
            text="Inversion Layer<br>(Saturation)",
            showarrow=False, font=dict(size=9, color='#27ae60'),
            bgcolor='#eafaf1', bordercolor='#27ae60', borderwidth=1
        )
    elif region == "Linear" and vgs_eff_plot > 0:
        fig_band.add_annotation(
            x=1.5, y=E0 + bend_ch - 0.15,
            text="Channel Formed<br>(Linear)",
            showarrow=False, font=dict(size=9, color='#f39c12'),
            bgcolor='#fef9e7', bordercolor='#f39c12', borderwidth=1
        )

    fig_band.update_layout(
        height=270, margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(
            tickvals=[0.5, 1.5, 2.5],
            ticktext=["Source", "Channel", "Drain"],
            tickfont=dict(size=10),
            showgrid=True, gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title="Energy (eV)", title_font=dict(size=10),
            showgrid=True, gridcolor='rgba(128,128,128,0.2)'
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99,
                    bgcolor="rgba(255,255,255,0.85)",
                    bordercolor="rgba(128,128,128,0.3)", borderwidth=1,
                    font=dict(size=9)),
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text=f"Energy Band Diagram ({device})",
                   font=dict(size=11), x=0.5, xanchor='center')
    )
    st.plotly_chart(fig_band, use_container_width=True, theme="streamlit")


# ── 3열: AI 해설 ─────────────────────────────────────────────
with col_right:
    st.markdown("### ☉ AI 해설")
    if "gemini_response" not in st.session_state:
        st.session_state.gemini_response = ""

    if not st.session_state.gemini_response:
        st.info("👉 왼쪽 패널에서 설정을 마치고 [AI 실시간 해설 보기] 버튼을 눌러보세요.")

    if ask_btn:
        question = (user_question.strip() if user_question.strip()
                    else f"현재 {device} MOSFET 조건에 대해 물리적으로 쉽게 설명해줘.")
        full_prompt = f"""
{device} MOSFET 조건 요약:
- V_GS = {vgs:.1f}V, V_DS = {vds:.1f}V, V_TH = {vth:.1f}V
- 현재 동작 영역: {region}
- 드레인 전류: {id_mA:.2f} mA
- 포화 전압: {vds_sat:.2f} V

사용자 질문: {question}

위의 소자 상태 데이터를 기반으로 전하 캐리어 이동 현상과 핀치오프 메커니즘을
전공자 관점에서 비유를 섞어 아주 쉽고 흥미롭게 한국어로 해설해줘. 4문장 내외로 마무리해줘.
        """
        with st.spinner("Gemini analyzing..."):
            st.session_state.gemini_response = call_gemini(full_prompt)

    if st.session_state.gemini_response:
        st.markdown("---")
        st.success(st.session_state.gemini_response)
