import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
import requests

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="MOSFET SIMULATOR",
    page_icon="🔌",
    layout="wide"
)

# ── CSS 스타일 ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Noto Sans KR', sans-serif; }
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2a2a4e !important;
        border-color: #555 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Gemini REST API 호출 (gRPC 완전 우회) ───────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP 오류: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"❌ API 통신 오류: {e}"

# ── 세션 상태 초기화 ─────────────────────────────────────────
for key, default in [("vth_val", 1.0), ("vgs_val", 2.6), ("vds_val", 3.7)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── 사이드바 제어 패널 ────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ 제어 및 입력 패널")
    st.divider()

    device = st.selectbox("소자 타입 선택", ["NMOS", "PMOS"])
    st.divider()

    # 1) 문턱 전압
    st.markdown("**문턱 전압 |V_TH| (V)**")
    vth = st.slider("V_TH", 0.0, 2.0,
                    value=float(st.session_state["vth_val"]),
                    step=0.1, key="vth_slide",
                    label_visibility="collapsed")
    st.session_state["vth_val"] = vth

    # 2) 게이트-소스 전압
    st.markdown("**게이트 전압 V_GS (V)**")
    vgs = st.slider("V_GS", 0.0, 5.0,
                    value=float(st.session_state["vgs_val"]),
                    step=0.1, key="vgs_slide",
                    label_visibility="collapsed")
    st.session_state["vgs_val"] = vgs

    # 3) 드레인-소스 전압
    st.markdown("**드레인 전압 V_DS (V)**")
    vds = st.slider("V_DS", 0.0, 5.0,
                    value=float(st.session_state["vds_val"]),
                    step=0.1, key="vds_slide",
                    label_visibility="collapsed")
    st.session_state["vds_val"] = vds

    st.divider()
    st.markdown("**🤖 ASK AI**")
    user_question = st.text_area(
        "", height=100,
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
            region = "Cutoff"; id_mA = 0.0
        elif vds < vgs_eff:
            region = "Linear"
            id_mA = Kn * (vgs_eff * vds - 0.5 * vds**2)
        else:
            region = "Saturation"
            id_mA = 0.5 * Kn * vgs_eff**2
    else:
        vgs_real = -vgs; vds_real = -vds; vth_real = -vth
        vgs_eff = vth_real - vgs_real
        vds_sat = max(vgs_eff, 0.0)
        if vgs_real > vth_real:
            region = "Cutoff"; id_mA = 0.0
        elif abs(vds_real) < vgs_eff:
            region = "Linear"
            id_mA = Kp * (vgs_eff * abs(vds_real) - 0.5 * abs(vds_real)**2)
        else:
            region = "Saturation"
            id_mA = 0.5 * Kp * vgs_eff**2
    return region, id_mA, vds_sat

region, id_mA, vds_sat = calc_mosfet(device, vgs, vds, vth)

# 한글 동작 영역명 (UI 표시용)
region_kr = {"Cutoff": "차단 영역 (Cutoff)",
             "Linear": "선형 영역 (Linear)",
             "Saturation": "포화 영역 (Saturation)"}.get(region, region)

# ── 타이틀 ──────────────────────────────────────────────────
st.markdown(f"# 🔌 {device} MOSFET SIMULATOR")
st.divider()

col_left, col_mid, col_right = st.columns([1, 1.4, 1])

# ── 1열: 소자 상태 + 구조 시각화 ─────────────────────────────
with col_left:
    st.markdown("### 📊 소자 상태")
    region_color = "#28a745" if region == "Saturation" else "#ffc107" if region == "Linear" else "#dc3545"
    st.markdown(f"""
    <div style='margin-bottom:8px'>
        <div style='font-size:13px;color:#666;margin-bottom:4px'>Operating Region</div>
        <div style='font-size:26px;font-weight:700;color:{region_color}'>{region_kr}</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("V_DS,sat" if device == "NMOS" else "|V_DS,sat|", f"{vds_sat:.2f} V")
    with c2:
        st.metric("I_D", f"{id_mA:.3f} mA")
    st.divider()

    st.markdown("### 📐 MOSFET 구조")
    fig_struct, ax = plt.subplots(figsize=(5, 4.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8.5); ax.axis("off")
    fig_struct.patch.set_facecolor('white')

    sub_color  = "#c8dff0" if device == "NMOS" else "#fce4d6"
    sub_edge   = "#5a8abf" if device == "NMOS" else "#e67e22"
    sub_text   = "p-Substrate" if device == "NMOS" else "n-Substrate"
    sub_tc     = "#2c5f8a" if device == "NMOS" else "#a04000"
    well_text  = "n+" if device == "NMOS" else "p+"
    well_color = "#4caf7d" if device == "NMOS" else "#9b59b6"
    well_edge  = "#2e7d52" if device == "NMOS" else "#8e44ad"
    carrier_color = "#e65100" if device == "NMOS" else "#8e44ad"
    ch_color   = "#66bb6a" if device == "NMOS" else "#d2b4de"
    ch_edge    = "#388e3c" if device == "NMOS" else "#af7ac5"

    sub = patches.FancyBboxPatch((0.3, 0.3), 9.4, 4.8,
                                 boxstyle="round,pad=0.1", fc=sub_color, ec=sub_edge, lw=1.5)
    ax.add_patch(sub)
    ax.text(5, 1.0, sub_text, ha="center", va="center",
            fontsize=10, color=sub_tc, fontstyle='italic')

    src = patches.FancyBboxPatch((0.5, 3.0), 2.3, 2.1,
                                 boxstyle="round,pad=0.05", fc=well_color, ec=well_edge, lw=1.5)
    ax.add_patch(src)
    ax.text(1.65, 4.1, "S", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white")
    ax.text(1.65, 3.35, well_text, ha="center", va="center", fontsize=10, color="#ffffff")

    drn = patches.FancyBboxPatch((7.2, 3.0), 2.3, 2.1,
                                 boxstyle="round,pad=0.05", fc=well_color, ec=well_edge, lw=1.5)
    ax.add_patch(drn)
    ax.text(8.35, 4.1, "D", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white")
    ax.text(8.35, 3.35, well_text, ha="center", va="center", fontsize=10, color="#ffffff")

    sio2 = patches.Rectangle((2.8, 5.1), 4.4, 0.4, fc="#e8e8e8", ec="#aaa", lw=1.0)
    ax.add_patch(sio2)
    ax.text(7.35, 5.3, "SiO2", ha="left", va="center", fontsize=8, color="#9400D3")

    gate = patches.FancyBboxPatch((2.8, 5.5), 4.4, 0.75,
                                  boxstyle="round,pad=0.05", fc="#37474f", ec="#1a1a2e", lw=1.5)
    ax.add_patch(gate)
    ax.text(5, 5.88, "Gate (G)", ha="center", va="center",
            fontsize=10, fontweight="bold", color="white")

    GATE_X_START, GATE_X_END = 2.8, 7.2
    GATE_LEN = GATE_X_END - GATE_X_START
    SIO2_BOTTOM, CH_THICK = 5.1, 0.5

    if region == "Saturation":
        ratio = float(np.clip(vds_sat / max(abs(vds), 0.01), 0.15, 0.85))
        po_x = GATE_X_START + GATE_LEN * ratio if device == "NMOS" \
               else GATE_X_END - GATE_LEN * ratio
        if device == "NMOS":
            tri_pts = np.array([[GATE_X_START, SIO2_BOTTOM],
                                [po_x, SIO2_BOTTOM],
