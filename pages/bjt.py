import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="BJT 시뮬레이터")

st.markdown("""
<style>
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] .element-container,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px !important;
        margin-top: 0px !important;
    }
    [data-testid="stSidebar"] h3 {
        font-size: 0.95rem !important;
        margin-bottom: 5px !important;
        margin-top: 5px !important;
    }
    [data-testid="stSidebar"] hr { margin: 6px 0 !important; }
    [data-testid="stSidebar"] .stSlider {
        margin-top: 0px !important;
        padding-bottom: 0px !important;
        margin-bottom: -10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {
        top: -30px !important;
    }
    [data-testid="stSidebar"] [data-testid="stSliderTickBar"] {
        margin-top: -20px !important;
    }
    [data-testid="stSidebar"] .stSelectbox {
        margin-top: -4px !important;
        margin-bottom: -4px !important;
    }
    [data-testid="stSidebar"] .stNumberInput div[data-baseweb="input"],
    [data-testid="stSidebar"] .stNumberInput div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stNumberInput input {
        height: 26px !important;
        padding: 1px 4px !important;
        font-size: 0.75rem !important;
        color: #2c3e50 !important;
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stTextArea {
        margin-top: 4px !important;
        margin-bottom: -4px !important;
    }
    [data-testid="stSidebar"] .stTextArea textarea {
        font-size: 0.78rem !important;
        padding: 5px !important;
        color: #2c3e50 !important;
    }

    /* 메인 영역 카드 스타일 (기존 유지) */
    .stat-card {
        background: #ffffff; border-radius: 12px; padding: 16px;
        border: 1px solid #eaeaea; box-shadow: 0px 4px 10px rgba(0,0,0,0.02); height: 100%;
    }
    .stat-title { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .stat-label { font-size: 0.7rem; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
    .stat-value { font-size: 1.15rem; font-weight: 700; color: #1e293b; }
    .section-header {
        font-size: 1.25rem; font-weight: 800; color: #334155;
        margin-top: 0px; margin-bottom: 12px;
        display: flex; align-items: center; gap: 8px;
    }
    .block-container { padding-top: 2.5rem !important; padding-bottom: 1rem !important; }
    .stPlotlyChart { margin-bottom: 15px !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("⬅ 홈으로 돌아가기", use_container_width=True):
        st.switch_page("app.py")

    st.markdown("### 🔬 제어 및 입력 패널")

    bjt_type = st.selectbox("소자 타입 선택", ["NPN", "PNP"])

    if "v_be_val" not in st.session_state: st.session_state.v_be_val = 0.75
    if "v_bc_val" not in st.session_state: st.session_state.v_bc_val = -2.80

    def update_be_slider(): st.session_state.v_be_val = st.session_state.be_num
    def update_be_num():    st.session_state.be_num   = st.session_state.v_be_val
    def update_bc_slider(): st.session_state.v_bc_val = st.session_state.bc_num
    def update_bc_num():    st.session_state.bc_num   = st.session_state.v_bc_val

    st.markdown("---")
    st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#1e293b;'>접합 전압 인가</span>", unsafe_allow_html=True)

    label_be = "베이스-에미터 전압 V_BE (V)" if bjt_type == "NPN" else "에미터-베이스 전압 V_EB (V)"
    st.markdown(f"<span style='font-size:0.75rem;font-weight:700;color:#2c3e50;'>{label_be}</span>", unsafe_allow_html=True)
    V_be = st.slider(label_be, min_value=-5.0, max_value=5.0, step=0.05,
                     key="v_be_val", on_change=update_be_num, label_visibility="collapsed")
    st.number_input(label_be, min_value=-5.0, max_value=5.0, step=0.05,
                    key="be_num", on_change=update_be_slider,
                    value=st.session_state.v_be_val, label_visibility="collapsed")

    label_bc = "베이스-컬렉터 전압 V_BC (V)" if bjt_type == "NPN" else "컬렉터-베이스 전압 V_CB (V)"
    st.markdown(f"<span style='font-size:0.75rem;font-weight:700;color:#2c3e50;margin-top:2px;display:block;'>{label_bc}</span>", unsafe_allow_html=True)
    V_bc = st.slider(label_bc, min_value=-5.0, max_value=5.0, step=0.1,
                     key="v_bc_val", on_change=update_bc_num, label_visibility="collapsed")
    st.number_input(label_bc, min_value=-5.0, max_value=5.0, step=0.1,
                    key="bc_num", on_change=update_bc_slider,
                    value=st.session_state.v_bc_val, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<span style='font-size:0.8rem;font-weight:700;color:#1e293b;'>💬 ASK AI</span>", unsafe_allow_html=True)
    user_question = st.text_area("질문 입력", height=60, label_visibility="collapsed",
                                 value="현재 바이어스 상태가 증폭기로서 왜 적합한지 밴드 다이어그램 관점에서 설명해줘.",
                                 placeholder="e.g. 현재 전압 조건 상태에 대해 물리적으로 쉽게 설명해줘.")
    ai_btn = st.button("⊙ AI 실시간 해설 보기", use_container_width=True)
    
# ── 물리량 계산
V_CC    = 5.0; R_C = 800.0; beta = 150; V_AF = 100.0
early_k = 1.0 / V_AF
be_fwd  = V_be > 0
bc_fwd  = V_bc > 0

if be_fwd and not bc_fwd:
    mode, mode_en, mode_color, anim_key = "순방향 활성 영역", "Forward Active", "#3b82f6", "forward_active"
    mode_desc = "B-E 순방향 + B-C 역방향 → 전자 확산 후 표류 → 증폭기 동작"
elif be_fwd and bc_fwd:
    mode, mode_en, mode_color, anim_key = "포화 영역", "Saturation", "#22c55e", "saturation"
    mode_desc = "양쪽 접합 순방향 → 장벽 소실 → 캐리어 범람 → 닫힌 스위치 (V_CE ≈ 0.2V)"
elif not be_fwd and bc_fwd:
    mode, mode_en, mode_color, anim_key = "역방향 활성 영역", "Reverse Active", "#a855f7", "reverse_active"
    mode_desc = "B-E 역방향 + B-C 순방향 → 흐름 역전 → 낮은 β"
else:
    mode, mode_en, mode_color, anim_key = "차단 영역", "Cutoff", "#ef4444", "cutoff"
    mode_desc = "양쪽 접합 역방향 → 장벽 최대 → 전류 차단 → OFF 상태 (스위치 개방)"

mode_full = f"{mode} ({mode_en})"
R_B_eff   = 30000.0
I_B_A     = max(0.0, V_be / R_B_eff) if be_fwd else 0.0

if mode_en == "Forward Active":
    I_C_ideal = beta * I_B_A
    I_C_max   = (V_CC - 0.2) / R_C
    q_ic_A    = max(0.0, min(I_C_ideal, I_C_max))
    q_vce     = max(0.2, V_CC - q_ic_A * R_C)
elif mode_en == "Saturation":
    q_vce = 0.2; q_ic_A = (V_CC - q_vce) / R_C
else:
    q_vce = V_CC; q_ic_A = 0.0

q_ic_mA = q_ic_A * 1000

# ── 테마 컬러 매핑 (파스텔톤)
if bjt_type == "NPN":
    e_bg, e_fg = "#e0f2fe", "#0ea5e9"
    b_bg, b_fg = "#ffe4e6", "#f43f5e"
    c_bg, c_fg = "#dcfce7", "#22c55e"
    e_txt, b_txt, c_txt = "N⁺", "P", "N"
else:
    e_bg, e_fg = "#ffe4e6", "#f43f5e"
    b_bg, b_fg = "#e0f2fe", "#0ea5e9"
    c_bg, c_fg = "#fce7f3", "#db2777"
    e_txt, b_txt, c_txt = "P⁺", "N", "P"

# ── 배터리 기호 생성 함수
def get_battery_svg(cx, cy, voltage, is_left_loop, color):
    if abs(voltage) < 0.01:
        return f'<line x1="{cx-20}" y1="{cy}" x2="{cx+20}" y2="{cy}" stroke="#1e293b" stroke-width="2"/>'
    
    pos_right = (voltage > 0) if is_left_loop else (voltage < 0)
    
    lines = [
        f'<line x1="{cx-20}" y1="{cy}" x2="{cx-8}" y2="{cy}" stroke="#1e293b" stroke-width="2"/>',
        f'<line x1="{cx+8}" y1="{cy}" x2="{cx+20}" y2="{cy}" stroke="#1e293b" stroke-width="2"/>'
    ]
    
    if pos_right: # [-  |+]
        lines.append(f'<line x1="{cx-5}" y1="{cy-10}" x2="{cx-5}" y2="{cy+10}" stroke="#1e293b" stroke-width="3"/>')
        lines.append(f'<line x1="{cx+5}" y1="{cy-15}" x2="{cx+5}" y2="{cy+15}" stroke="#1e293b" stroke-width="1.5"/>')
        lines.append(f'<text x="{cx-14}" y="{cy-16}" font-family="sans-serif" font-weight="bold" font-size="16" fill="{color}">-</text>')
        lines.append(f'<text x="{cx+14}" y="{cy-16}" font-family="sans-serif" font-weight="bold" font-size="16" fill="{color}">+</text>')
    else: # [+  |-]
        lines.append(f'<line x1="{cx-5}" y1="{cy-15}" x2="{cx-5}" y2="{cy+15}" stroke="#1e293b" stroke-width="1.5"/>')
        lines.append(f'<line x1="{cx+5}" y1="{cy-10}" x2="{cx+5}" y2="{cy+10}" stroke="#1e293b" stroke-width="3"/>')
        lines.append(f'<text x="{cx-14}" y="{cy-16}" font-family="sans-serif" font-weight="bold" font-size="16" fill="{color}">+</text>')
        lines.append(f'<text x="{cx+14}" y="{cy-16}" font-family="sans-serif" font-weight="bold" font-size="16" fill="{color}">-</text>')
        
    return "".join(lines)

# ── BJT 구조 SVG (반응형 Width 적용)
def make_bjt_svg(bjt_type, V_be, V_bc):
    is_npn = bjt_type == "NPN"
    
    be_str = f"V_BE={V_be:.2f}V ({'순방향' if V_be > 0 else '역방향'})" if is_npn else f"V_EB={V_be:.2f}V ({'순방향' if V_be > 0 else '역방향'})"
    bc_str = f"V_BC={V_bc:.2f}V ({'순방향' if V_bc > 0 else '역방향'})" if is_npn else f"V_CB={V_bc:.2f}V ({'순방향' if V_bc > 0 else '역방향'})"

    bat_be = get_battery_svg(110, 150, V_be, True, e_fg)
    bat_bc = get_battery_svg(270, 150, V_bc, False, b_fg)

    svg = f"""
    <svg width="100%" height="auto" viewBox="0 0 400 200" style="display:block; margin:auto; background:#ffffff;">
        <style>
            .region-title {{ font-family: sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
            .region-sub {{ font-family: sans-serif; font-size: 11px; text-anchor: middle; }}
            .term-text {{ font-family: serif; font-size: 16px; font-weight: bold; fill: #1e293b; dominant-baseline: middle; }}
            .voltage-text {{ font-family: sans-serif; font-size: 12px; font-weight: bold; text-anchor: middle; }}
            .line-style {{ stroke: #1e293b; stroke-width: 1.5; fill: none; }}
        </style>

        <rect x="60" y="30" width="90" height="45" fill="{e_bg}" stroke="{e_fg}" stroke-width="1.5"/>
        <text x="105" y="48" class="region-title" fill="{e_fg}">{e_txt}</text>
        <text x="105" y="65" class="region-sub" fill="{e_fg}">Emitter</text>
        
        <rect x="150" y="30" width="60" height="45" fill="{b_bg}" stroke="{b_fg}" stroke-width="1.5"/>
        <text x="180" y="48" class="region-title" fill="{b_fg}">{b_txt}</text>
        <text x="180" y="65" class="region-sub" fill="{b_fg}">Base</text>
        
        <rect x="210" y="30" width="100" height="45" fill="{c_bg}" stroke="{c_fg}" stroke-width="1.5"/>
        <text x="260" y="48" class="region-title" fill="{c_fg}">{c_txt}</text>
        <text x="260" y="65" class="region-sub" fill="{c_fg}">Collector</text>
        
        <line x1="60" y1="52" x2="20" y2="52" class="line-style"/>
        <text x="5" y="54" class="term-text">E</text>
        
        <line x1="310" y1="52" x2="350" y2="52" class="line-style"/>
        <text x="360" y="54" class="term-text">C</text>
        
        <line x1="180" y1="75" x2="180" y2="150" class="line-style"/>
        <text x="180" y="20" class="term-text" style="text-anchor: middle;">B</text>
        
        <line x1="20" y1="52" x2="20" y2="150" class="line-style"/>
        <line x1="20" y1="150" x2="90" y2="150" class="line-style"/>
        {bat_be}
        <text x="110" y="175" class="voltage-text" fill="{e_fg}">{be_str}</text>
        <line x1="130" y1="150" x2="180" y2="150" class="line-style"/>
        
        <line x1="350" y1="52" x2="350" y2="150" class="line-style"/>
        <line x1="350" y1="150" x2="290" y2="150" class="line-style"/>
        {bat_bc}
        <text x="270" y="175" class="voltage-text" fill="{b_fg}">{bc_str}</text>
        <line x1="250" y1="150" x2="180" y2="150" class="line-style"/>
    </svg>
    """
    return svg

bjt_svg = make_bjt_svg(bjt_type, V_be, V_bc)

# ════════════════════════════════════════════════
# 레이아웃: 메인 타이틀 & 3단 컬럼 배치 (스크린샷 매칭)
# ════════════════════════════════════════════════

st.markdown(f"""
<h1 style='text-align:left; font-size:2.2rem; font-weight:900; color:#1e293b; margin-top:0; padding-bottom:12px; border-bottom:1px solid #e2e8f0; margin-bottom: 24px;'>
    🔌 {bjt_type} BJT SIMULATOR
</h1>
""", unsafe_allow_html=True)

# 3단 컬럼 비율: 30% (상태+구조), 46% (그래프), 24% (AI)
col1, col2, col3 = st.columns([0.28, 0.46, 0.26], gap="medium")

# ── 1열: 소자 상태 & 구조
with col1:
    st.markdown("<div class='section-header'>📊 소자 상태</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='stat-card' style='margin-bottom: 24px;'>
        <div class='stat-title'>Operating Region</div>
        <div style='font-size:1.6rem; font-weight:800; color:{mode_color}; line-height:1.2; margin-bottom:4px;'>
            {mode}
        </div>
        <div style='font-size:0.9rem; color:{mode_color}; margin-bottom:18px; font-weight:600;'>({mode_en})</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px;'>
            <div>
                <div class='stat-label'>인가전압 |V_CE|</div>
                <div class='stat-value'>{abs(V_be - V_bc):.2f} V</div>
            </div>
            <div>
                <div class='stat-label'>컬렉터전류 I_C</div>
                <div class='stat-value'>{q_ic_mA:.2f} mA</div>
            </div>
            <div>
                <div class='stat-label'>베이스전류 I_B</div>
                <div class='stat-value'>{I_B_A*1e6:.1f} μA</div>
            </div>
            <div>
                <div class='stat-label'>Q점 V_CEQ</div>
                <div class='stat-value'>{q_vce:.2f} V</div>
            </div>
        </div>
        <div style='margin-top:20px; padding:12px 14px; background:#f8fafc;
                    border-left:4px solid {mode_color}; border-radius:6px;
                    font-size:0.78rem; font-weight:700; color:#334155; line-height:1.45;'>
            <span style='color:{mode_color}'>{mode_desc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>📐 BJT 구조</div>", unsafe_allow_html=True)
    canvas_html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; gap:8px;">
      <div style="background:#ffffff; border:none; width:100%;">
        {bjt_svg}
      </div>
      <canvas id="bjtCanvas" width="400" height="130"
              style="background:#ffffff; border-radius:8px; display:block;
                     box-shadow:0 2px 8px rgba(0,0,0,0.06); width:100%;"></canvas>
      <p style="color:#64748b; font-size:0.85rem; margin:0; font-family:sans-serif; text-align:center; font-weight:bold;">
          <span style="color:#06b6d4;">● 전자 (Electron)</span>
          &nbsp;&nbsp;&nbsp;
          <span style="color:#f97316;">● 정공 (Hole)</span>
      </p>
    </div>

    <script>
    (function() {{
        const canvas = document.getElementById('bjtCanvas');
        const ctx    = canvas.getContext('2d');
        const MODE     = '{anim_key}';
        const BJT_TYPE = '{bjt_type}';
        const W = canvas.width, H = canvas.height;

        const N_e = 35, N_h = 35;
        let particles = [];

        for (let i = 0; i < N_e; i++) {{
            particles.push({{ x: Math.random()*W, y: 30+Math.random()*70, r:3.5, type:'electron', dir:Math.random()<0.5?1:-1 }});
        }}
        for (let i = 0; i < N_h; i++) {{
            particles.push({{ x: Math.random()*W, y: 30+Math.random()*70, r:3.5, type:'hole', dir:Math.random()<0.5?1:-1 }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, W, H);

            ctx.fillStyle='{e_bg}'; ctx.fillRect(0,0,130,H);
            ctx.fillStyle='{b_bg}'; ctx.fillRect(130,0,160,H);
            ctx.fillStyle='{c_bg}'; ctx.fillRect(290,0,W-290,H);

            [130, 290].forEach(x => {{
                ctx.strokeStyle='#cbd5e1'; ctx.lineWidth=2;
                ctx.setLineDash([4,4]);
                ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
                ctx.setLineDash([]);
            }});

            ctx.font='bold 11px sans-serif';
            const labels = BJT_TYPE==='NPN'
                ? ['Emitter (N+)','Base (P)','Collector (N)']
                : ['Emitter (P+)','Base (N)','Collector (P)'];
            ctx.fillStyle='{e_fg}'; ctx.fillText(labels[0], 8, 20);
            ctx.fillStyle='{b_fg}'; ctx.fillText(labels[1], 138, 20);
            ctx.fillStyle='{c_fg}'; ctx.fillText(labels[2], 298, 20);

            particles.forEach(p => {{
                ctx.fillStyle   = p.type==='electron' ? '#06b6d4' : '#f97316';
                ctx.shadowBlur  = 3; ctx.shadowColor = ctx.fillStyle;
                ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI*2); ctx.fill();
                ctx.shadowBlur  = 0;

                let vx=0, scatterX=0.2;

                if (MODE==='forward_active') {{
                    if (BJT_TYPE==='NPN') {{
                        if (p.type==='electron') {{ vx=3.5; if(p.x>W) p.x=0; }}
                        else                     {{ vx=-1.5; if(p.x<0) p.x=290; }}
                    }} else {{
                        if (p.type==='hole')     {{ vx=3.5; if(p.x>W) p.x=0; }}
                        else                     {{ vx=-1.5; if(p.x<0) p.x=290; }}
                    }}
                }} else if (MODE==='saturation') {{
                    if (BJT_TYPE==='NPN') {{
                        if (p.type==='electron') {{
                            vx=p.dir*3.5; if(vx>0 && p.x>W) p.x=0; if(vx<0 && p.x<0) p.x=W;
                        }} else {{
                            vx=p.dir*1.5; if(vx>0 && p.x>W) p.x=210; if(vx<0 && p.x<0) p.x=210;
                        }}
                    }} else {{
                        if (p.type==='hole') {{
                            vx=p.dir*3.5; if(vx>0 && p.x>W) p.x=0; if(vx<0 && p.x<0) p.x=W;
                        }} else {{
                            vx=p.dir*1.5; if(vx>0 && p.x>W) p.x=210; if(vx<0 && p.x<0) p.x=210;
                        }}
                    }}
                }} else if (MODE==='reverse_active') {{
                    if (BJT_TYPE==='NPN') {{
                        if (p.type==='electron') {{ vx=-3.5; if(p.x<0) p.x=W; }}
                        else                     {{ vx=1.5;  if(p.x>W) p.x=130; }}
                    }} else {{
                        if (p.type==='hole')     {{ vx=-3.5; if(p.x<0) p.x=W; }}
                        else                     {{ vx=1.5;  if(p.x>W) p.x=130; }}
                    }}
                }} else {{
                    vx=0; scatterX=0.8;
                }}

                p.x += vx + (Math.random()-0.5)*scatterX;
                p.y += (Math.random()-0.5)*0.8;
                if (p.y<30)  p.y=H-10;
                if (p.y>H-5) p.y=30;
            }});
            requestAnimationFrame(draw);
        }}
        draw();
    }})();
    </script>
    """
    components.html(canvas_html, height=400)

# ── 2열: 그래프 모음 (I-V & 밴드)
with col2:
    st.markdown("<div class='section-header'>📈 특성 곡선 & 밴드 다이어그램</div>", unsafe_allow_html=True)
    
    # ── I_C–V_CE 특성 곡선
    fig_iv = go.Figure()
    sign       = 1 if bjt_type=="NPN" else -1
    v_arr      = np.linspace(0, V_CC+0.8, 300)
    ib_list    = [10,20,30,40,50]
    base_color = (249, 115, 22) if bjt_type=="NPN" else (168, 85, 247)

    for idx, ib_uA in enumerate(ib_list):
        ib_A   = ib_uA*1e-6
        ic_sat = beta*ib_A*1000
        alpha  = 0.4 + 0.12*idx
        color  = f"rgba({base_color[0]},{base_color[1]},{base_color[2]},{alpha:.2f})"
        ic_curve = [max(0.0, ic_sat*np.tanh(v/0.12)*(1+early_k*v)) for v in v_arr]
        fig_iv.add_trace(go.Scatter(
            x=[sign*v for v in v_arr], y=[sign*ic for ic in ic_curve],
            mode='lines', line=dict(color=color,width=2.5),
            name=f"I_B={ib_uA}μA", showlegend=True))

    sat_ic_mag = (V_CC/R_C)*1000
    fig_iv.add_trace(go.Scatter(
        x=[0.0, sign*V_CC], y=[sign*sat_ic_mag, 0.0],
        mode='lines', line=dict(color='#0f172a',width=3), name='직류 부하선'))
    fig_iv.add_vline(x=sign*0.2, line=dict(color='#ef4444',width=1.5,dash='dash'))

    q_x, q_y = sign*q_vce, sign*q_ic_mA
    fig_iv.add_trace(go.Scatter(
        x=[q_x], y=[q_y], mode='markers+text',
        marker=dict(color='#ef4444',size=10,symbol='circle',line=dict(color='white',width=2)),
        text=[f"Q ({sign*q_vce:.2f}V, {sign*q_ic_mA:.2f}mA)"],
        textposition="top left" if bjt_type=="NPN" else "bottom right", 
        textfont=dict(size=11,color='#dc2626',weight='bold'), name="Q점"))
    
    fig_iv.update_layout(
        title=dict(text="I-V Characteristic Curve", font=dict(size=12, color="#64748b"), x=0.5, y=0.95),
        xaxis_title="V_CE [V]", yaxis_title="I_C [mA]",
        xaxis=dict(range=[-0.2, V_CC+1.2] if bjt_type=="NPN" else [-(V_CC+1.2), 0.2], showgrid=True, gridcolor='#f1f5f9', zeroline=True, zerolinecolor='#475569', zerolinewidth=1.5),
        yaxis=dict(range=[-0.5, sat_ic_mag+1.5] if bjt_type=="NPN" else [-(sat_ic_mag+1.5), 0.5], showgrid=True, gridcolor='#f1f5f9', zeroline=True, zerolinecolor='#475569', zerolinewidth=1.5),
        height=320, margin=dict(l=10,r=10,t=40,b=10), showlegend=True,
        legend=dict(x=0.75 if bjt_type=="NPN" else 0.02, y=0.98 if bjt_type=="NPN" else 0.15,
                    bgcolor='rgba(255,255,255,0.9)', bordercolor='#cbd5e1', borderwidth=1, font=dict(size=9)),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_iv, use_container_width=True)

    # ── 에너지 밴드 다이어그램 (물리적 오류 완전 수정)
    fig_band = go.Figure()
    E_g = 1.12
    x_all = np.linspace(0, 8.0, 400)
    ec_all = np.zeros_like(x_all)

    v_be_eff = float(np.clip(V_be, -5.0, 0.75))
    v_bc_eff = float(np.clip(V_bc, -5.0, 0.75))

    if bjt_type == "NPN":
        E_F_Base = 0.0; E_V_Base = -0.1; E_C_Base = E_V_Base + E_g
        E_F_Emitter = E_F_Base + v_be_eff; E_F_Collector = E_F_Base + v_bc_eff
        E_C_Emitter = E_F_Emitter - 0.05
        # 물리적 수정: N형 Collector는 E_C가 E_F보다 살짝 위쪽에 있어야 함
        E_C_Collector = E_F_Collector + 0.15 
    else:
        E_F_Base = 0.0; E_C_Base = 0.1; E_V_Base = E_C_Base - E_g
        E_F_Emitter = E_F_Base - v_be_eff; E_F_Collector = E_F_Base - v_bc_eff
        E_V_Emitter = E_F_Emitter + 0.05
        # 물리적 수정: P형 Collector는 E_V가 E_F보다 살짝 아래쪽에 있어야 함
        E_V_Collector = E_F_Collector - 0.15 
        E_C_Emitter = E_V_Emitter + E_g
        E_C_Collector = E_V_Collector + E_g

    for i, x in enumerate(x_all):
        if   x <= 2.4: ec_all[i] = E_C_Emitter
        elif x >= 5.6: ec_all[i] = E_C_Collector
        elif 3.2 <= x <= 4.8: ec_all[i] = E_C_Base
        elif 2.4 < x < 3.2:
            t = (x-2.4)/0.8*np.pi
            ec_all[i] = E_C_Emitter + (E_C_Base-E_C_Emitter)*(1-np.cos(t))/2
        elif 4.8 < x < 5.6:
            t = (x-4.8)/0.8*np.pi
            ec_all[i] = E_C_Base + (E_C_Collector-E_C_Base)*(1-np.cos(t))/2
    ev_all = ec_all - E_g

    c_bg_e = "rgba(224,242,254,0.8)" if bjt_type=="NPN" else "rgba(255,228,230,0.8)"
    c_bg_b = "rgba(255,228,230,0.8)" if bjt_type=="NPN" else "rgba(224,242,254,0.8)"
    c_bg_c = "rgba(220,252,231,0.8)" if bjt_type=="NPN" else "rgba(252,231,243,0.8)"

    fig_band.add_vrect(x0=0,   x1=2.8, fillcolor=c_bg_e, line_width=0, layer="below")
    fig_band.add_vrect(x0=2.8, x1=5.2, fillcolor=c_bg_b, line_width=0, layer="below")
    fig_band.add_vrect(x0=5.2, x1=8.0, fillcolor=c_bg_c, line_width=0, layer="below")
    
    fig_band.add_trace(go.Scatter(x=x_all, y=ec_all, mode='lines', line=dict(color='#0f172a',width=3), name='E_c'))
    fig_band.add_trace(go.Scatter(x=x_all, y=ev_all, mode='lines', line=dict(color='#0f172a',width=3), name='E_v'))
    
    fig_band.add_trace(go.Scatter(x=[0,2.4],   y=[E_F_Emitter,E_F_Emitter],   mode='lines', line=dict(color='#3b82f6',width=2,dash='dash'), name='E_F(E)'))
    fig_band.add_trace(go.Scatter(x=[3.2,4.8], y=[E_F_Base,E_F_Base],         mode='lines', line=dict(color='#3b82f6',width=2,dash='dash'), name='E_F(B)'))
    fig_band.add_trace(go.Scatter(x=[5.6,8.0], y=[E_F_Collector,E_F_Collector],mode='lines', line=dict(color='#3b82f6',width=2,dash='dash'), name='E_F(C)'))
    
    fig_band.add_annotation(x=8.15, y=ec_all[-1], text="<b>E_c</b>", showarrow=False, font=dict(size=12,color='#0f172a'))
    fig_band.add_annotation(x=8.15, y=ev_all[-1], text="<b>E_v</b>", showarrow=False, font=dict(size=12,color='#0f172a'))

    np.random.seed(42)
    c_elec = '#06b6d4' 
    c_hole = '#f97316' 
    
    if bjt_type == "NPN":
        fig_band.add_trace(go.Scatter(x=np.random.uniform(0.2,2.2,16), y=E_C_Emitter+np.random.uniform(0.02,0.15,16), mode='markers', marker=dict(color=c_elec,size=9,line=dict(color='#0891b2',width=1.5)), showlegend=False))
        fig_band.add_trace(go.Scatter(x=np.random.uniform(3.4,4.6,10), y=E_V_Base-np.random.uniform(0.02,0.15,10), mode='markers', marker=dict(color=c_hole,size=10,line=dict(color='#ea580c',width=1.5)), showlegend=False))
        fig_band.add_trace(go.Scatter(x=np.random.uniform(5.8,7.8,12), y=E_C_Collector+np.random.uniform(0.02,0.15,12), mode='markers', marker=dict(color=c_elec,size=9,line=dict(color='#0891b2',width=1.5)), showlegend=False))
    else:
        fig_band.add_trace(go.Scatter(x=np.random.uniform(0.2,2.2,16), y=E_V_Emitter-np.random.uniform(0.02,0.15,16), mode='markers', marker=dict(color=c_hole,size=10,line=dict(color='#ea580c',width=1.5)), showlegend=False))
        fig_band.add_trace(go.Scatter(x=np.random.uniform(3.4,4.6,10), y=E_C_Base+np.random.uniform(0.02,0.15,10), mode='markers', marker=dict(color=c_elec,size=9,line=dict(color='#0891b2',width=1.5)), showlegend=False))
        fig_band.add_trace(go.Scatter(x=np.random.uniform(5.8,7.8,12), y=E_V_Collector-np.random.uniform(0.02,0.15,12), mode='markers', marker=dict(color=c_hole,size=10,line=dict(color='#ea580c',width=1.5)), showlegend=False))

    fig_band.add_vline(x=2.8, line=dict(color='#94a3b8',width=1.5,dash='dot'))
    fig_band.add_vline(x=5.2, line=dict(color='#94a3b8',width=1.5,dash='dot'))
    fig_band.update_layout(
        title=dict(text=f"Energy Band Diagram [{bjt_type}]", font=dict(size=12, color="#64748b"), x=0.5, y=0.95),
        xaxis=dict(visible=False, range=[-0.2,8.6]),
        yaxis=dict(visible=False, range=[min(ev_all)-0.35, max(ec_all)+0.8]),
        height=320, margin=dict(l=10,r=10,t=40,b=10), showlegend=False, plot_bgcolor='white'
    )
    st.plotly_chart(fig_band, use_container_width=True)

# ── 3열: AI 해설
with col3:
    st.markdown("<div class='section-header'>⊙ AI 해설</div>", unsafe_allow_html=True)
    if ai_btn:
        system_instruction = f"""
당신은 반도체 소자 물리학 및 증폭 회로 설계 전문가입니다.
인삿말 없이 바로 수치 분석부터 시작하세요.
현재 설정: BJT={bjt_type}, V_BE={V_be:.2f}V, V_BC={V_bc:.2f}V
모드={mode_full}, I_B={I_B_A*1e6:.2f}μA, I_C={q_ic_mA:.2f}mA, Q점 V_CE={q_vce:.2f}V
6주차 에너지 밴드 교안과 7주차 바이어스 교안을 연결하여 한국어 마크다운으로 답변하세요.
질문: "{user_question}"
"""
        if "GEMINI_API_KEY" in st.secrets:
            with st.spinner("AI가 분석 중입니다..."):
                try:
                    import google.generativeai as genai
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    resp  = model.generate_content(system_instruction)
                    st.markdown(f"""
                    <div style='background:#ffffff; padding:16px; border-radius:10px;
                                border:1px solid #e2e8f0; font-size:0.85rem; color:#1e293b;
                                height:640px; overflow-y:auto; line-height:1.6; box-shadow: 0px 4px 6px rgba(0,0,0,0.02);'>
                        {resp.text}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"오류: {e}")
        else:
            st.error("GEMINI_API_KEY가 설정되지 않았습니다.")
    else:
        st.markdown(f"""
        <div style='background:#f0f9ff; padding:16px; border-radius:10px;
                    border:1px solid #bae6fd; font-size:0.88rem; font-weight:600;
                    color:#0369a1; display:flex; align-items:flex-start; gap:8px;'>
            <span>👉</span>
            <span>왼쪽 패널에서 설정을 마치고 [AI 실시간 해설 보기] 버튼을 눌러보세요.</span>
        </div>
        """, unsafe_allow_html=True)
