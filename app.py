# ==============================================================================
# app.py  —  Streamlit 진입점 (오케스트레이션만 담당)
# ==============================================================================
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO

from config import GROUP_COLORS
from models import model_A, model_B
from ui_components import styled_df, kpi_card, render_waterfall, build_table
from ui_sidebar import render_sidebar
from ui_group_editor import render_group_editor
from ui_model_guide import render_model_guide
# app.py  —  Streamlit 진입점 (오케스트레이션만 담당)
#
# 실행: streamlit run app.py
#
# 의존 모듈:
#   config.py            상수 (COL_IDX, MONTH_KR, GROUP_COLORS)
#   data_loader.py       load_excel, groups_to_json_bytes, json_bytes_to_groups
#   models.py            aggregate, model_A, model_B
#   ui_components.py     styled_df, kpi_card, render_waterfall, build_table
#   ui_sidebar.py        render_sidebar → 사이드바 전체
#   ui_group_selector.py render_group_selector → 그룹 카드 UI
#   ui_model_guide.py    render_model_guide → 하단 모델 비교표
# ==============================================================================



# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="매출 차이 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

/* ── 전역 폰트 & 배경 ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    letter-spacing: -0.01em;
}
.stApp {
    background-color: #0f0f1e !important;
}
[data-testid="stAppViewContainer"] > section.main {
    background-color: #0f0f1e !important;
}
.block-container {
    background-color: #0f0f1e !important;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* ── 사이드바 스타일 ── */
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    background-color: #13132a !important;
    border-right: 1px solid rgba(124,58,237,0.15) !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] > div {
    background-color: #13132a !important;
    overflow-x: hidden !important;
}
[data-testid="stSidebar"] .block-container {
    background-color: #13132a !important;
    padding: 1.2rem 0.9rem !important;
    overflow-x: hidden !important;
    max-width: 100% !important;
}
/* 파일 업로더 컴팩트 — 텍스트 줄바꿈 허용 */
[data-testid="stFileUploaderDropzone"] {
    padding: 8px 10px !important;
    min-height: 58px !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    font-size: 0.68rem !important;
    white-space: normal !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
}
/* 사이드바 내 모든 텍스트 overflow 방지 */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.78rem !important;
    white-space: normal !important;
    word-break: break-word !important;
}
/* period badge — 작게 */
.period-badge {
    font-size: 0.64rem !important;
    padding: 2px 6px !important;
    white-space: nowrap !important;
    white-space: nowrap;
}

/* ── Streamlit 기본 UI 제거 ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── 버튼 ── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    background-color: rgba(124,58,237,0.08) !important;
    color: #c4b5fd !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    padding: 6px 14px !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    border-color: #7c3aed !important;
    background-color: rgba(124,58,237,0.18) !important;
    color: #ede9fe !important;
    box-shadow: 0 0 12px rgba(124,58,237,0.25) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    border-color: #7c3aed !important;
    color: #ffffff !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.5) !important;
}

/* ── selectbox / multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    border-radius: 8px !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    background-color: rgba(124,58,237,0.06) !important;
    color: #e2e8f0 !important;
    font-size: 0.82rem !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}

/* ── radio ── */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
}

/* ── file uploader ── */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed rgba(124,58,237,0.3) !important;
    border-radius: 12px !important;
    background: rgba(124,58,237,0.05) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #7c3aed !important;
    background: rgba(124,58,237,0.1) !important;
    box-shadow: 0 0 16px rgba(124,58,237,0.15) !important;
}

/* ── expander ── */
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    background-color: rgba(124,58,237,0.06) !important;
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-radius: 10px !important;
    color: #c4b5fd !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stExpander"] summary:hover {
    border-color: #7c3aed !important;
    background-color: rgba(124,58,237,0.12) !important;
    box-shadow: 0 0 10px rgba(124,58,237,0.15) !important;
}
[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    background: rgba(124,58,237,0.03) !important;
}

/* ── 탭 ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(124,58,237,0.2) !important;
    gap: 0 !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    color: #64748b !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #7c3aed !important;
    font-weight: 600 !important;
    background: transparent !important;
}
[data-baseweb="tab"]:hover {
    color: #a78bfa !important;
    background: rgba(124,58,237,0.08) !important;
}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.02) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(124,58,237,0.12) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: rgba(124,58,237,0.08) !important;
    color: #7c3aed !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(124,58,237,0.2) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(124,58,237,0.06) !important;
}

/* ── caption / info ── */
[data-testid="stCaptionContainer"], .stCaption {
    color: #475569 !important;
    font-size: 0.72rem !important;
}

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(124,58,237,0.3);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(124,58,237,0.5);
}

/* ── 커스텀 컴포넌트 ── */
.main-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.6px;
    margin-bottom: 0;
}
.main-subtitle {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 400;
    margin-bottom: 1.6rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.section-header {
    font-size: 1.0rem;
    font-weight: 700;
    color: #c4b5fd;
    letter-spacing: 0.01em;
    text-transform: none;
    padding: 0 0 9px 14px;
    border-left: 3px solid #7c3aed;
    margin: 2rem 0 1.1rem 0;
    background: none;
}

/* KPI 카드 — 글래스모피즘 */
.kpi-card {
    border-radius: 14px;
    padding: 18px 20px 16px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(124,58,237,0.2);
}
.kpi-card-neutral { border-top: 2px solid #7c3aed; }
.kpi-card-pos     { border-top: 2px solid #10b981; }
.kpi-card-neg     { border-top: 2px solid #f43f5e; }
.kpi-card-zero    { border-top: 2px solid #334155; }

.kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 4px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.kpi-formula {
    font-size: 0.6rem;
    color: #334155;
    margin-bottom: 8px;
    font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
    display: inline-block;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1.15;
}
.kpi-val-neutral { color: #f1f5f9; }
.kpi-val-pos     { color: #34d399; }
.kpi-val-neg     { color: #f87171; }
.kpi-val-zero    { color: #475569; }

.period-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.7rem;
    font-weight: 500;
    margin: 2px 3px;
    letter-spacing: 0.02em;
}
.badge-base {
    background: rgba(71,85,105,0.2);
    color: #94a3b8;
    border: 1px solid rgba(71,85,105,0.3);
}
.badge-curr {
    background: rgba(124,58,237,0.15);
    color: #a78bfa;
    border: 1px solid rgba(124,58,237,0.3);
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 사이드바
# ==============================================================================
ctx = render_sidebar()   # → dict with df_all, df_base, df_curr, labels, model, show_detail

df_all         = ctx["df_all"]
df_base        = ctx["df_base"]
df_curr        = ctx["df_curr"]
base_label     = ctx["base_label"]
curr_label     = ctx["curr_label"]
period_mode    = ctx["period_mode"]
analysis_model = ctx["analysis_model"]
show_detail    = ctx["show_detail"]
is_ytd         = ctx.get("is_ytd", False)

# ==============================================================================
# 타이틀
# ==============================================================================
st.markdown(
    '<div class="main-title">매출 차이 분석</div>'
    '<div class="main-subtitle">Variance Analysis Dashboard</div>',
    unsafe_allow_html=True)

if df_all is None:
    st.info("👈 왼쪽 사이드바에서 **ERP 매출실적 파일**을 업로드하세요.")
    with st.expander("📋 엑셀 파일 컬럼 구성 안내"):
        col_info = pd.DataFrame({
            "열":  ["D","I","V","W","AB","AD","AE","AF","AI","AJ","AN","AO","BC"],
            "내용": ["매출일(YYYY-MM-DD)","매출처명","품목코드","품목명","단위",
                     "수량","환종(KRW/USD)","환율","(외화)판매단가","(외화)판매금액",
                     "(장부단가)원화환산판매단가","(장부금액)원화환산판매금액",
                     "품목계정(제품/상품/원재료/부재료/제조-수선비)"],
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
    st.stop()

# ==============================================================================
# 품목 그룹 설정 (편집 테이블) — 접기/펼치기
# ==============================================================================
with st.expander("📂 품목 그룹 설정  (클릭하여 펼치기 / 접기)", expanded=False):
    render_group_editor(df_all)

# ── 선택된 모델 배너 ──────────────────────────────────────────────────────────
is_model_A   = "모델 A" in analysis_model
accent_color = "#4472c4" if is_model_A else "#e6812a"
badge_bg     = "#eef4ff" if is_model_A else "#fff8ee"

if is_model_A:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;
                background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.25);
                border-radius:12px;padding:12px 16px;margin-bottom:14px;">
      <div style="width:4px;height:36px;background:linear-gradient(180deg,#7c3aed,#a78bfa);
                  border-radius:2px;flex-shrink:0;"></div>
      <div style="flex:1;">
        <div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;margin-bottom:3px;">모델 A — 원인별 임팩트 분석</div>
        <div style="font-size:0.68rem;color:#475569;font-family:'SF Mono','Fira Code',monospace;letter-spacing:0.02em;">
          ① (Q1−Q0)×P0_fx×ER0 &nbsp;│&nbsp; ② (P1−P0)×Q1×ER0 &nbsp;│&nbsp; ③ (ER1−ER0)×Q1×P1_fx
        </div>
      </div>
      <span style="font-size:0.65rem;font-weight:600;background:rgba(124,58,237,0.2);color:#a78bfa;
                   border:1px solid rgba(124,58,237,0.3);border-radius:6px;padding:3px 10px;
                   white-space:nowrap;letter-spacing:0.04em;">재무·감사 표준</span>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;
                background:rgba(251,146,60,0.06);border:1px solid rgba(251,146,60,0.2);
                border-radius:12px;padding:12px 16px;margin-bottom:14px;">
      <div style="width:4px;height:36px;background:linear-gradient(180deg,#f97316,#fb923c);
                  border-radius:2px;flex-shrink:0;"></div>
      <div style="flex:1;">
        <div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;margin-bottom:3px;">모델 B — 활동별 증분 분석</div>
        <div style="font-size:0.68rem;color:#475569;font-family:'SF Mono','Fira Code',monospace;letter-spacing:0.02em;">
          ① Q↑×P1_krw / Q↓×P0_krw &nbsp;│&nbsp; ② 총차이−①−③ &nbsp;│&nbsp; ③ P/Q 4-Case
        </div>
      </div>
      <span style="font-size:0.65rem;font-weight:600;background:rgba(249,115,22,0.15);color:#fb923c;
                   border:1px solid rgba(249,115,22,0.3);border-radius:6px;padding:3px 10px;
                   white-space:nowrap;letter-spacing:0.04em;">영업·전략 보고</span>
    </div>""", unsafe_allow_html=True)

# ── 기간 유효성 ───────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
if df_base.empty and df_curr.empty:
    st.error("두 기간 모두 데이터가 없습니다.")
    st.stop()

# ── 차이 분석 실행 ────────────────────────────────────────────────────────────
with st.spinner("분석 중..."):
    va, va_detail = model_A(df_base, df_curr) if is_model_A else model_B(df_base, df_curr)

# ==============================================================================
# 분석 대상 선택 — 커스텀 그룹 기준
# ==============================================================================
all_items    = sorted(va["품목명"].unique())
item_mapping = st.session_state.get("item_mapping", {})

# item_mapping → groups 구성 (커스텀 그룹 우선, 미분류 후순위)
custom_groups: dict = {}
for item in all_items:
    grp = item_mapping.get(item, "").strip()
    if grp:
        custom_groups.setdefault(grp, []).append(item)

unassigned = [i for i in all_items if not item_mapping.get(i, "").strip()]

# 전체 groups (커스텀 + 미분류)
groups: dict = dict(custom_groups)
if unassigned:
    groups["미분류"] = unassigned

has_custom = len(custom_groups) > 0

# 그룹 내 품목 매출 합산 → 내림차순 정렬
def _grp_rev(gn):
    items = custom_groups.get(gn, [])
    sub = va[va["품목명"].isin(items)]
    return sub["매출1"].sum() if not sub.empty else 0

custom_group_names = sorted(custom_groups.keys(), key=_grp_rev, reverse=True)
# groups도 정렬 순서 반영
_sorted_groups = {gn: custom_groups[gn] for gn in custom_group_names}
if unassigned:
    _sorted_groups["미분류"] = unassigned
groups = _sorted_groups
group_names = list(groups.keys())

st.markdown('<div class="section-header">📦 분석 대상 선택</div>', unsafe_allow_html=True)

if has_custom:
    # ── 커스텀 그룹 체크박스 key 초기화 (최초 1회 + 새 그룹 자동 추가) ────────
    if "known_custom_groups" not in st.session_state:
        st.session_state["known_custom_groups"] = set()
    for gn in group_names:
        ck = f"chk_grp_{gn}"
        if ck not in st.session_state:
            # 신규 그룹은 기본 체크
            st.session_state[ck] = True
    # 사라진 그룹의 키 정리
    for old_gn in list(st.session_state["known_custom_groups"]):
        if old_gn not in group_names:
            st.session_state.pop(f"chk_grp_{old_gn}", None)
    st.session_state["known_custom_groups"] = set(group_names)

    # ── 전체 선택/해제 버튼 ──────────────────────────────────────────────────
    _sel_cnt = sum(1 for gn in group_names if st.session_state.get(f"chk_grp_{gn}", True))
    with st.expander(f"📦 그룹 선택 — {_sel_cnt} / {len(group_names)}개  ▾", expanded=False):
        _c1, _c2 = st.columns(2)
        with _c1:
            if st.button("전체 선택", key="sel_all_grp", use_container_width=True):
                for gn in group_names:
                    st.session_state[f"chk_grp_{gn}"] = True
                st.rerun()
        with _c2:
            if st.button("전체 해제", key="sel_none_grp", use_container_width=True):
                for gn in group_names:
                    st.session_state[f"chk_grp_{gn}"] = False
                st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        for gi, gn in enumerate(group_names):
            # key만 사용, value= 미사용 → 무한루프 완전 차단
            st.checkbox(gn, key=f"chk_grp_{gn}")

    selected_groups = [gn for gn in group_names if st.session_state.get(f"chk_grp_{gn}", True)]
    selected_items  = [item for gn in selected_groups for item in groups.get(gn, [])]

else:
    # ── 커스텀 그룹 없는 경우: 품목 체크박스 ────────────────────────────────
    for item in all_items:
        ck = f"chk_item_{item}"
        if ck not in st.session_state:
            st.session_state[ck] = True

    _sel_cnt2 = sum(1 for i in all_items if st.session_state.get(f"chk_item_{i}", True))
    with st.expander(f"📋 품목 선택 — {_sel_cnt2} / {len(all_items)}개  ▾", expanded=False):
        _c1, _c2 = st.columns(2)
        with _c1:
            if st.button("전체 선택", key="sel_all_items", use_container_width=True):
                for item in all_items:
                    st.session_state[f"chk_item_{item}"] = True
                st.rerun()
        with _c2:
            if st.button("전체 해제", key="sel_none_items", use_container_width=True):
                for item in all_items:
                    st.session_state[f"chk_item_{item}"] = False
                st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        for item in all_items:
            st.checkbox(item, key=f"chk_item_{item}")

    selected_items  = [i for i in all_items if st.session_state.get(f"chk_item_{i}", True)]
    selected_groups = []

if not selected_items:
    st.warning("그룹 또는 품목을 1개 이상 선택하세요.")
    st.stop()

va_filtered        = va[va["품목명"].isin(selected_items)].copy()
va_detail_filtered = va_detail[va_detail["품목명"].isin(selected_items)].copy()

# ==============================================================================
# KPI 요약
# ==============================================================================
st.markdown('<div class="section-header">📈 종합 요약</div>', unsafe_allow_html=True)

total_base = va_filtered["매출0"].sum()
total_curr = va_filtered["매출1"].sum()
total_diff = va_filtered["총차이"].sum()
qty_v      = va_filtered["수량차이"].sum()
price_v    = va_filtered["단가차이"].sum()
fx_v       = va_filtered["환율차이"].sum()
all_krw    = va_filtered["is_krw"].all() if "is_krw" in va_filtered.columns else False

growth_pct = (total_diff / total_base * 100) if total_base != 0 else 0
qty_pct    = (qty_v   / abs(total_base) * 100) if total_base != 0 else 0
price_pct  = (price_v / abs(total_base) * 100) if total_base != 0 else 0
fx_pct     = (fx_v    / abs(total_base) * 100) if total_base != 0 else 0
diff_color  = "#34d399" if total_diff >= 0 else "#f87171"
diff_bg     = "rgba(52,211,153,0.08)" if total_diff >= 0 else "rgba(248,113,113,0.08)"
diff_border = "rgba(52,211,153,0.3)"  if total_diff >= 0 else "rgba(248,113,113,0.3)"
diff_arrow  = "+" if total_diff >= 0 else ""

# ── 상단: 기준/실적/총차이 3열 ────────────────────────────────────────────────
st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px;">
  <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
              border-top:2px solid #7c3aed;border-radius:12px;padding:16px 18px;">
    <div style="font-size:0.62rem;font-weight:600;color:#475569;letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:5px;">기준 매출</div>
    <div style="font-size:0.7rem;color:#475569;margin-bottom:6px;">{base_label}</div>
    <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">
      {total_base/1e8:,.1f}<span style="font-size:0.78rem;color:#64748b;margin-left:4px;">억원</span></div>
    <div style="font-size:0.68rem;color:#334155;margin-top:3px;">{total_base:,.0f}원</div>
  </div>
  <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
              border-top:2px solid #0ea5e9;border-radius:12px;padding:16px 18px;">
    <div style="font-size:0.62rem;font-weight:600;color:#475569;letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:5px;">실적 매출</div>
    <div style="font-size:0.7rem;color:#475569;margin-bottom:6px;">{curr_label}</div>
    <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0;letter-spacing:-0.03em;">
      {total_curr/1e8:,.1f}<span style="font-size:0.78rem;color:#64748b;margin-left:4px;">억원</span></div>
    <div style="font-size:0.68rem;color:#334155;margin-top:3px;">{total_curr:,.0f}원</div>
  </div>
  <div style="background:{diff_bg};border:1px solid {diff_border};
              border-top:2px solid {diff_color};border-radius:12px;padding:16px 18px;">
    <div style="font-size:0.62rem;font-weight:600;color:#475569;letter-spacing:0.1em;
                text-transform:uppercase;margin-bottom:5px;">총 차이 (①+②+③)</div>
    <div style="font-size:0.7rem;color:#475569;margin-bottom:6px;">실적 - 기준</div>
    <div style="font-size:1.5rem;font-weight:700;color:{diff_color};letter-spacing:-0.03em;">
      {diff_arrow}{total_diff/1e8:,.1f}<span style="font-size:0.78rem;margin-left:4px;">억원</span></div>
    <div style="font-size:0.68rem;color:{diff_color};opacity:0.8;margin-top:3px;">
      {diff_arrow}{total_diff:,.0f}원 ({growth_pct:+.1f}%)</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 요인 분해 바 ─────────────────────────────────────────────────────────────
max_abs = max(abs(qty_v), abs(price_v), abs(fx_v), 1)

def _factor_row(num, label, formula, val):
    clr = "#34d399" if val >= 0 else "#f87171"
    bgc = "rgba(52,211,153,0.06)" if val >= 0 else "rgba(248,113,113,0.06)"
    bdr = "rgba(52,211,153,0.18)" if val >= 0 else "rgba(248,113,113,0.18)"
    w   = min(100, abs(val) / max(abs(max_abs), 1) * 100)
    pct = val / abs(total_base) * 100 if total_base != 0 else 0
    sgn = "+" if val >= 0 else ""
    return (
        f'<div style="background:{bgc};border:1px solid {bdr};border-radius:10px;'
        f'padding:11px 15px;margin-bottom:6px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">'
        f'<div><span style="font-size:0.75rem;font-weight:600;color:#94a3b8;">{num} {label}</span>'
        f'<span style="font-size:0.62rem;color:#334155;margin-left:10px;font-family:\'SF Mono\',monospace;">{formula}</span></div>'
        f'<div style="text-align:right;">'
        f'<span style="font-size:1.0rem;font-weight:700;color:{clr};">{sgn}{val/1e6:,.1f}M</span>'
        f'<span style="font-size:0.65rem;color:{clr};opacity:0.8;margin-left:6px;">{pct:+.1f}%</span>'
        f'</div></div>'
        f'<div style="height:4px;background:rgba(255,255,255,0.05);border-radius:2px;">'
        f'<div style="height:4px;width:{w:.1f}%;background:{clr};border-radius:2px;opacity:0.75;"></div>'
        f'</div></div>'
    )

fx_display = 0.0 if all_krw else fx_v
if is_model_A:
    rows_html = (
        _factor_row("①", "수량 차이", "(Q1-Q0)xP0_fxxER0", qty_v) +
        _factor_row("②", "단가 차이", "(P1-P0)xQ1xER0", price_v) +
        _factor_row("③", "환율 차이", "KRW 해당없음" if all_krw else "(ER1-ER0)xQ1xP1_fx", fx_display)
    )
else:
    rows_html = (
        _factor_row("①", "수량 차이 (Volume)", "Q+:xP1_krw / Q-:xP0_krw", qty_v) +
        _factor_row("②", "단가 차이 (Residual)", "총차이-①-③", price_v) +
        _factor_row("③", "환율 차이 (FX)", "KRW 해당없음" if all_krw else "4-Case", fx_display)
    )
st.markdown(rows_html, unsafe_allow_html=True)

# ── AI 분석 제언 ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="section-header">🤖 AI 분석 제언</div>',
    unsafe_allow_html=True
)

# 파라미터 변경 시 결과 초기화
_ai_key = f"{base_label}|{curr_label}|{period_mode}|{analysis_model}|{','.join(sorted(selected_items[:15]))}"
if st.session_state.get("_ai_param_key") != _ai_key:
    st.session_state["_ai_param_key"] = _ai_key
    st.session_state.pop("_ai_result", None)

if st.button("✨ AI 분석 시작", key="btn_ai_analysis", type="primary"):
    st.session_state.pop("_ai_result", None)
    _grp_str  = ", ".join(selected_groups) if selected_groups else "전체"
    _item_str = ", ".join(sorted(selected_items)[:20])
    _prompt = (
        "당신은 매출 차이 분석 전문 애널리스트입니다. 아래 데이터를 바탕으로 경영진을 위한 "
        "간결하고 통찰력 있는 분석 제언을 한국어로 작성하세요.\n\n"
        f"[분석 파라미터]\n"
        f"- 비교 기간: {base_label} vs {curr_label}\n"
        f"- 비교 방식: {period_mode}\n"
        f"- 분석 모델: {analysis_model}\n"
        f"- 분석 대상: {_grp_str}\n\n"
        f"[분석 수치]\n"
        f"- 기준 매출: {total_base:,.0f}원\n"
        f"- 실적 매출: {total_curr:,.0f}원\n"
        f"- 총 차이: {total_diff:+,.0f}원 ({growth_pct:+.1f}%)\n"
        f"- 수량 차이: {qty_v:+,.0f}원 ({qty_pct:+.1f}%)\n"
        f"- 단가 차이: {price_v:+,.0f}원 ({price_pct:+.1f}%)\n"
        f"- 환율 차이: {fx_v:+,.0f}원 ({fx_pct:+.1f}%)\n"
        f"- 품목: {_item_str}\n\n"
        "아래 구조로 작성하세요:\n"
        "**핵심 요약**: 가장 중요한 변화 한 문장\n"
        "**주요 성과**: 긍정적인 부분 (2문장)\n"
        "**주의 사항**: 우려되는 부분 (2문장)\n"
        "**제언**: 구체적 액션 아이템 2개\n"
    )
    # API 키: Streamlit Cloud → Settings → Secrets → [anthropic] api_key = "sk-ant-..."
    import os as _os
    _api_key = (st.secrets.get("anthropic", {}).get("api_key", "")
               or _os.environ.get("ANTHROPIC_API_KEY", ""))
    import requests as _req
    if not _api_key:
        st.session_state["_ai_result"] = ("⚠️ API 키 미설정\n"
            "Streamlit Cloud → Settings → Secrets 에 추가:\n\n"
            "[anthropic]\napi_key = \"sk-ant-api03-...\"\n")
    else:
        with st.spinner("AI 분석 중..."):
            try:
                _resp = _req.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": _api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    json={"model": "claude-sonnet-4-20250514", "max_tokens": 800,
                          "messages": [{"role": "user", "content": _prompt}]},
                    timeout=60,
                )
                _data = _resp.json()
                if "error" in _data:
                    raise Exception(_data["error"].get("message", str(_data["error"])))
                _text = "".join(
                    b.get("text","") for b in _data.get("content",[])
                    if b.get("type") == "text"
                )
                st.session_state["_ai_result"] = _text if _text else "분석 결과를 받지 못했습니다."
            except Exception as _e:
                st.session_state["_ai_result"] = f"⚠️ 오류: {_e}"

if "_ai_result" in st.session_state:
    st.markdown(
        f'<div style="background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.2);'
        f'border-radius:12px;padding:18px 22px;font-size:0.83rem;color:#cbd5e1;line-height:1.75;">'
        f'{st.session_state["_ai_result"].replace(chr(10),"<br>")}'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(124,58,237,0.2);'
        'border-radius:12px;padding:20px;text-align:center;color:#334155;font-size:0.8rem;">'
        'AI 분석 시작 버튼을 눌러 분석 결과를 확인하세요<br>'
        '<span style="font-size:0.7rem;color:#1e293b;">파라미터(기간/모델/품목)가 변경되면 결과가 초기화됩니다</span></div>',
        unsafe_allow_html=True
    )


# ==============================================================================
# 커스텀 그룹별 차이 분석  (기본 분석 화면)
# ==============================================================================
st.markdown('<div class="section-header">📋 커스텀 그룹별 차이 분석</div>', unsafe_allow_html=True)


# ── 세부 품목 표 렌더 헬퍼 (합계 행 분리, 행 너비 통일) ─────────────────────────
def _show_split_table(df_with_total: "pd.DataFrame", money_cols: list):
    """
    build_table() 반환값을 데이터 표 + 합계 표로 분리 렌더링.
    column_config로 동일한 컬럼 너비를 두 표에 모두 적용해 정렬 통일.
    """
    ROW_H = 36
    HDR_H = 40

    total_mask = df_with_total.apply(
        lambda r: any("합 계" in str(v) for v in r.values), axis=1
    )
    data_df  = df_with_total[~total_mask].reset_index(drop=True)
    total_df = df_with_total[total_mask].reset_index(drop=True)

    # ── 공통 column_config 생성 ───────────────────────────────────────────────
    # 품목명/그룹 등 텍스트 열은 너비 고정, 숫자 열은 동일 width
    def _make_col_config(df):
        cfg = {}
        for col in df.columns:
            if col in money_cols:
                cfg[col] = st.column_config.NumberColumn(col, format="%,.0f", width="medium")
            elif col in ("품목명", "그룹", "환종"):
                cfg[col] = st.column_config.TextColumn(col, width="large")
            else:
                cfg[col] = st.column_config.TextColumn(col, width="small")
        return cfg

    col_cfg = _make_col_config(data_df)

    # 데이터 표
    data_h = min(520, max(HDR_H + ROW_H, len(data_df) * ROW_H + HDR_H))
    st.dataframe(
        styled_df(data_df, money_cols),
        use_container_width=True,
        hide_index=True,
        height=data_h,
        column_config=col_cfg,
    )

    # 합계 표 — 동일한 column_config 적용으로 열 너비 통일
    if not total_df.empty:
        def _total_style(df):
            def color(v):
                try:
                    fv = float(v)
                    if fv < 0: return "color:#c0392b;font-weight:700"
                    if fv > 0: return "color:#1a7a4a;font-weight:700"
                except: pass
                return "font-weight:700"
            fmt = {c: "{:,.0f}" for c in money_cols if c in df.columns}
            styler = df.style.format(fmt, na_rep="-")
            for c in df.columns:
                fn = color if c in money_cols else (lambda v: "font-weight:700")
                styler = styler.applymap(fn, subset=[c])
            return styler

        st.dataframe(
            _total_style(total_df),
            use_container_width=True,
            hide_index=True,
            height=HDR_H + ROW_H,
            column_config=col_cfg,
        )

# ── 그룹별 표 + 드롭다운 헬퍼 ───────────────────────────────────────────────
def _render_group_section(grp_list, grp_map, color_map, va_src, va_detail_src, sel_key):
    """
    ① 상단: 드롭다운 selectbox (어느 그룹 세부 품목을 볼지 선택)
    ② 중단: 그룹별 요약 표 (행=그룹, 열=기준매출/실적매출/총차이/①②③)
    ③ 하단: 선택된 그룹의 품목별 상세 테이블
    """
    if not grp_list:
        st.info("표시할 그룹이 없습니다.")
        return

    # ① 드롭다운 (상단 배치)
    dropdown_opts = ["전체 합산"] + grp_list
    selected_drp = st.selectbox(
        "세부 품목 드릴다운",
        options=dropdown_opts,
        index=0,
        key=sel_key,
    )

    # ② 그룹별 요약 표 데이터 구성 (합계는 마지막 행)
    all_items_in = [i for gn in grp_list for i in grp_map.get(gn, [])]
    tot = va_src[va_src["품목명"].isin(all_items_in)]
    bl = base_label; cl = curr_label

    data_rows = []
    for gn in grp_list:
        items = grp_map.get(gn, [])
        if not items:
            continue
        g_va = va_src[va_src["품목명"].isin(items)]
        data_rows.append({
            "그룹": f"📦 {gn}  ({len(items)}개 품목)",
            f"기준매출 [{bl}]": g_va["매출0"].sum(),
            f"실적매출 [{cl}]": g_va["매출1"].sum(),
            "총차이(원)":  g_va["총차이"].sum(),
            "①수량차이":  g_va["수량차이"].sum(),
            "②단가차이":  g_va["단가차이"].sum(),
            "③환율차이":  g_va["환율차이"].sum(),
            "_is_total": False,
        })

    total_row = {
        "그룹": "【합 계】",
        f"기준매출 [{bl}]": tot["매출0"].sum(),
        f"실적매출 [{cl}]": tot["매출1"].sum(),
        "총차이(원)":  tot["총차이"].sum(),
        "①수량차이":  tot["수량차이"].sum(),
        "②단가차이":  tot["단가차이"].sum(),
        "③환율차이":  tot["환율차이"].sum(),
        "_is_total": True,
    }

    # 정렬 state: 컬럼 클릭 시 데이터 행만 정렬, 합계 행은 항상 마지막
    sort_key = f"{sel_key}_sort"
    sort_col = st.session_state.get(sort_key, None)
    sort_asc = st.session_state.get(f"{sort_key}_asc", True)

    tbl_df_data = pd.DataFrame(data_rows)
    money_c = [c for c in tbl_df_data.columns if c not in ("그룹", "_is_total")]

    if sort_col and sort_col in tbl_df_data.columns:
        tbl_df_data = tbl_df_data.sort_values(sort_col, ascending=sort_asc)

    # 데이터 행만 포함한 표 (정렬 가능)
    tbl_df = tbl_df_data.drop(columns=["_is_total"])

    def _style_data(df):
        def color(v):
            try:
                fv = float(v)
                if fv < 0: return "color:#c0392b;font-weight:600"
                if fv > 0: return "color:#1a7a4a;font-weight:600"
            except: pass
            return ""
        diff_cols = ["총차이(원)", "①수량차이", "②단가차이", "③환율차이"]
        fmt = {c: "{:,.0f}" for c in money_c}
        styler = df.style.format(fmt, na_rep="-")
        for c in diff_cols:
            if c in df.columns:
                styler = styler.applymap(color, subset=[c])
        return styler

    st.dataframe(
        _style_data(tbl_df),
        use_container_width=True,
        hide_index=True,
        height=min(460, max(80, len(tbl_df)*36+40)),
    )

    # 합계 행 — 별도 고정 테이블 (정렬 영향 없음)
    total_df = pd.DataFrame([{
        k: v for k, v in total_row.items() if k != "_is_total"
    }])

    def _style_total(df):
        def color(v):
            try:
                fv = float(v)
                if fv < 0: return "color:#c0392b;font-weight:700"
                if fv > 0: return "color:#1a7a4a;font-weight:700"
            except: pass
            return "font-weight:700"
        diff_cols = ["총차이(원)", "①수량차이", "②단가차이", "③환율차이"]
        fmt = {c: "{:,.0f}" for c in money_c}
        styler = df.style.format(fmt, na_rep="-")
        for c in df.columns:
            styler = styler.applymap(
                (lambda v: color(v)) if c in diff_cols else (lambda v: "font-weight:700"),
                subset=[c]
            )
        return styler

    st.dataframe(
        _style_total(total_df),
        use_container_width=True,
        hide_index=True,
        height=70,
    )

    # ③ 선택된 그룹의 품목별 상세
    if selected_drp == "전체 합산":
        drp_items = all_items_in
        clr2 = "#1e293b"
        title = f"전체 합산 — 품목별 상세 ({len(drp_items)}개)"
    else:
        drp_items = grp_map.get(selected_drp, [])
        clr2 = color_map.get(selected_drp, "#1e40af")
        title = f"📦 {selected_drp} — 세부 품목 ({len(drp_items)}개)"

    if drp_items:
        st.markdown(
            f'<div style="background:{clr2};border-radius:7px;padding:6px 14px;'
            f'color:white;font-size:0.82rem;font-weight:700;margin:8px 0 6px 0;">'
            f'{title}</div>',
            unsafe_allow_html=True)
        drp_va = va_src[va_src["품목명"].isin(drp_items)]
        drp_vd = va_detail_src[va_detail_src["품목명"].isin(drp_items)]
        dtbl, dmc = build_table(
            drp_vd if show_detail else drp_va,
            base_label, curr_label, show_detail)
        _show_split_table(dtbl, dmc)


# ── va_disp_total 항상 정의 (다운로드용) ─────────────────────────────────────
va_disp_total, money_cols = build_table(
    va_detail_filtered if show_detail else va_filtered,
    base_label, curr_label, show_detail)

if has_custom and selected_groups:
    grp_colors = {
        gn: GROUP_COLORS[i % len(GROUP_COLORS)][0]
        for i, gn in enumerate(list(groups.keys()))
        if gn != "미분류"
    }
    sel_grp_map = {gn: [i for i in groups.get(gn, []) if i in selected_items]
                   for gn in selected_groups}
    _render_group_section(selected_groups, sel_grp_map, grp_colors,
                          va_filtered, va_detail_filtered, "drp_main")
else:
    _show_split_table(va_disp_total, money_cols)

# ==============================================================================
# 품목계정 분류별 차이 분석 (제품 / 상품 / 기타)
# — 각 탭 안에서 커스텀 그룹 단위로 표시, 세부 품목은 드롭다운
# ==============================================================================
if "품목계정_분류" in df_all.columns:
    st.markdown('<div class="section-header">🗂️ 품목계정별 차이 분석</div>', unsafe_allow_html=True)
    st.caption("제품 / 상품 / 기타(원재료·부재료·제조-수선비) 기준 집계 — 각 탭은 커스텀 그룹 단위로 표시")

    acct_map = (
        df_all[["품목명", "품목계정_분류"]]
        .drop_duplicates(subset=["품목명"])
        .set_index("품목명")["품목계정_분류"].to_dict()
    )
    ACCT_CATS   = ["제품", "상품", "기타"]
    ACCT_COLORS = {"제품": "#1e40af", "상품": "#065f46", "기타": "#7c3aed"}

    # ── KPI 카드 (제품/상품/기타 합산) ────────────────────────────────────────
    acct_cols = st.columns(3)
    for ci, cat in enumerate(ACCT_CATS):
        cat_items = [i for i in selected_items if acct_map.get(i,"기타") == cat]
        sub  = va_filtered[va_filtered["품목명"].isin(cat_items)]
        c_b  = sub["매출0"].sum(); c_c = sub["매출1"].sum()
        c_d  = sub["총차이"].sum()
        c_q  = sub["수량차이"].sum(); c_p = sub["단가차이"].sum(); c_f = sub["환율차이"].sum()
        clr  = ACCT_COLORS[cat]
        d_s  = "▲ +" if c_d >= 0 else "▼ "
        d_cl = "#16a34a" if c_d >= 0 else "#dc2626"
        acct_cols[ci].markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-top:2px solid {clr};
                    border-radius:10px;padding:14px 16px;">
          <div style="font-size:0.82rem;font-weight:800;color:{clr};margin-bottom:8px;">{cat}</div>
          <div style="font-size:0.65rem;color:#475569;letter-spacing:0.06em;text-transform:uppercase;">기준 매출</div>
          <div style="font-size:0.95rem;font-weight:600;color:#e2e8f0;margin-bottom:5px;">{c_b:,.0f}원</div>
          <div style="font-size:0.65rem;color:#475569;letter-spacing:0.06em;text-transform:uppercase;">실적 매출</div>
          <div style="font-size:0.95rem;font-weight:600;color:#e2e8f0;margin-bottom:5px;">{c_c:,.0f}원</div>
          <div style="font-size:0.65rem;color:#475569;letter-spacing:0.06em;text-transform:uppercase;">총 차이</div>
          <div style="font-size:1.08rem;font-weight:900;color:{d_cl};">{d_s}{c_d:,.0f}원</div>
          <div style="font-size:0.68rem;color:#94a3b8;margin-top:4px;">
            ① {c_q:+,.0f} ② {c_p:+,.0f} ③ {c_f:+,.0f}
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── 탭별 커스텀 그룹 테이블 ────────────────────────────────────────────────
    acct_tab_list = st.tabs(["전체"] + ACCT_CATS)

    for ti, cat_label in enumerate(["전체"] + ACCT_CATS):
        with acct_tab_list[ti]:
            if cat_label == "전체":
                tab_items = selected_items
            else:
                tab_items = [i for i in selected_items if acct_map.get(i,"기타") == cat_label]

            if not tab_items:
                st.info(f"{cat_label} 분류의 데이터가 없습니다.")
                continue

            if has_custom and selected_groups:
                # 커스텀 그룹 단위로 표시
                # 해당 탭 품목이 속한 그룹만 추려서 표시
                tab_grp_map = {}
                for gn in selected_groups:
                    grp_tab_items = [i for i in groups.get(gn,[]) if i in tab_items]
                    if grp_tab_items:
                        tab_grp_map[gn] = grp_tab_items
                tab_grp_list = list(tab_grp_map.keys())

                grp_colors_acct = {
                    gn: GROUP_COLORS[i % len(GROUP_COLORS)][0]
                    for i, gn in enumerate(list(groups.keys()))
                    if gn != "미분류"
                }
                tab_va  = va_filtered[va_filtered["품목명"].isin(tab_items)]
                tab_vd  = va_detail_filtered[va_detail_filtered["품목명"].isin(tab_items)]
                _render_group_section(tab_grp_list, tab_grp_map, grp_colors_acct,
                                     tab_va, tab_vd, f"drp_acct_{cat_label}")
            else:
                # 커스텀 그룹 없으면 품목명 단위 테이블
                sub_va = va_filtered[va_filtered["품목명"].isin(tab_items)].copy()
                sub_vd = va_detail_filtered[va_detail_filtered["품목명"].isin(tab_items)].copy()
                tbl, mc = build_table(sub_vd if show_detail else sub_va,
                                      base_label, curr_label, show_detail)
                _show_split_table(tbl, mc)


# ==============================================================================
# 시각화
# ==============================================================================
st.markdown('<div class="section-header">📊 차이 구성 요소 시각화</div>', unsafe_allow_html=True)

try:
    import plotly.graph_objects as go

    tab_wf, tab_bar = st.tabs(["🌊 Waterfall (전체 합산)", "📊 품목별 총차이"])

    with tab_wf:
        # ── 상단: 분석 대상 + 단위 선택 한 줄 배치 ───────────────────────────
        _top_left, _top_right = st.columns([5, 1])

        with _top_left:
            if has_custom and selected_groups:
                _n = len(selected_groups)
                _total_items = sum(len(groups.get(gn, [])) for gn in selected_groups)
                # 그룹이 많으면 개별 태그 대신 요약 텍스트로
                if _n <= 4:
                    _grp_parts = " · ".join(
                        f'<span style="color:{GROUP_COLORS[i % len(GROUP_COLORS)][0]};font-weight:600;">{gn}</span>'
                        for i, gn in enumerate(selected_groups)
                    )
                    _summary = f'<span style="color:#475569;font-size:0.72rem;">{_grp_parts}</span>'
                else:
                    _first3 = " · ".join(
                        f'<span style="color:{GROUP_COLORS[i % len(GROUP_COLORS)][0]};font-weight:600;">{gn}</span>'
                        for i, gn in enumerate(selected_groups[:3])
                    )
                    _summary = (
                        f'<span style="color:#475569;font-size:0.72rem;">{_first3}'
                        f'<span style="color:#334155;"> 외 {_n-3}개 그룹</span></span>'
                    )
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
                    f'<span style="font-size:0.6rem;font-weight:600;color:#475569;'
                    f'letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;">분석 대상</span>'
                    f'<span style="color:rgba(255,255,255,0.1);">|</span>'
                    f'{_summary}'
                    f'<span style="font-size:0.65rem;color:#334155;margin-left:4px;">({_total_items}개 품목)</span>'
                    f'</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="font-size:0.72rem;color:#475569;padding:6px 0;">'
                    f'전체 품목 {len(selected_items)}개</div>',
                    unsafe_allow_html=True)

        with _top_right:
            _wf_unit = st.radio(
                "단위",
                ["M원", "원"],
                index=0,
                horizontal=True,
                key="wf_unit_sel",
            )
        # radio 값 매핑
        _wf_unit_real = "백만원" if _wf_unit == "M원" else "원"

        fig_wf = render_waterfall(total_base, qty_v, price_v, fx_v,
                                  total_curr, base_label, curr_label, accent_color,
                                  unit=_wf_unit_real)
        st.plotly_chart(fig_wf, use_container_width=True)

        with st.expander("🔢 Waterfall 계산 근거 데이터", expanded=False):
            sign = lambda v: f"+{v:,.0f}" if v >= 0 else f"{v:,.0f}"
            pct  = lambda v, base: f"({v/base*100:+.1f}%)" if base != 0 else ""

            calc_rows = [
                {"구분": "기준 매출",   "금액 (원)": f"{total_base:,.0f}",
                 "설명": f"{base_label} 원화매출 합계", "비고": ""},
                {"구분": "① 수량 차이", "금액 (원)": sign(qty_v),
                 "설명": "수량 변동에 의한 매출 증감",
                 "비고": "기준단가×수량변화" if is_model_A else "실적/기준단가×수량변화"},
                {"구분": "② 단가 차이", "금액 (원)": sign(price_v),
                 "설명": "단가 변동에 의한 매출 증감",
                 "비고": "(P실적−P기준)×Q실적×ER기준" if is_model_A else "총차이−①−③"},
                {"구분": "③ 환율 차이", "금액 (원)": sign(fx_v),
                 "설명": "환율 변동에 의한 매출 증감",
                 "비고": "(ER실적−ER기준)×Q실적×P실적_fx" if is_model_A else "4-Case 분기"},
                {"구분": "실적 매출",   "금액 (원)": f"{total_curr:,.0f}",
                 "설명": f"{curr_label} 원화매출 합계", "비고": ""},
                {"구분": "▶ 총 차이",   "금액 (원)": sign(total_diff),
                 "설명": f"실적−기준 {pct(total_diff, total_base)}",
                 "비고": "①+②+③ = 총차이 검증"},
            ]
            calc_df = pd.DataFrame(calc_rows)
            check   = abs((qty_v + price_v + fx_v) - total_diff) < 1
            st.markdown(
                f'<div style="background:{"#d4edda" if check else "#f8d7da"};border-radius:6px;'
                f'padding:7px 14px;font-size:0.8rem;font-weight:700;'
                f'color:{"#155724" if check else "#721c24"};margin-bottom:8px;">'
                f'{"✅ 항등식 검증 통과: ①+②+③ = 총차이 (" + sign(qty_v+price_v+fx_v) + "원)" if check else "⚠️ 항등식 오차 발생"}'
                f'</div>', unsafe_allow_html=True)
            st.dataframe(calc_df, use_container_width=True, hide_index=True)

            # 품목×환종 상세
            st.markdown("**품목별 구성요소 상세 (환종 분리)**")
            st.caption("KRW행: 원화단가만 표시 / USD행: 외화단가·환율 표시")
            dr = va_detail_filtered.copy()
            dr["검증"] = dr.apply(
                lambda r: "✅" if abs(
                    round(r["수량차이"]+r["단가차이"]+r["환율차이"]) - round(r["총차이"])
                ) < 1 else f"⚠️ {round(r['수량차이']+r['단가차이']+r['환율차이'])-round(r['총차이']):+,.0f}",
                axis=1
            )
            krw_mask = dr["is_krw"] == True
            for col_name in ["P0_fx","P1_fx","ER0","ER1"]:
                if col_name in dr.columns:
                    dr.loc[krw_mask, col_name] = np.nan

            col_map = [("품목명","품목명"),("환종","환종"),("매출1","실적매출(원)"),
                       ("Q1","실적수량"),("P1_krw","실적단가(원화)"),("P1_fx","실적단가(외화)"),
                       ("ER1","실적환율"),("매출0","기준매출(원)"),("Q0","기준수량"),
                       ("P0_krw","기준단가(원화)"),("P0_fx","기준단가(외화)"),("ER0","기준환율"),
                       ("총차이","총차이(원)"),("수량차이","①수량차이(원)"),
                       ("단가차이","②단가차이(원)"),("환율차이","③환율차이(원)"),("검증","검증")]
            seen, sel_src, sel_dst = set(), [], []
            for src, dst in col_map:
                if src in dr.columns and src not in seen:
                    seen.add(src); sel_src.append(src); sel_dst.append(dst)
            detail_df = dr[sel_src].rename(columns=dict(zip(sel_src, sel_dst)))

            str_cols   = {"품목명","환종","검증"}
            num_cols_d = [c for c in detail_df.columns
                          if c not in str_cols and pd.api.types.is_numeric_dtype(detail_df[c])]
            sidx = len(detail_df)
            detail_df.loc[sidx, "품목명"] = "【합 계】"
            detail_df.loc[sidx, "환종"]   = ""
            detail_df.loc[sidx, "검증"]   = ""
            sum_target = [c for c in num_cols_d if not any(kw in c for kw in ["단가","환율"])]
            for c in sum_target:
                detail_df.loc[sidx, c] = detail_df[c].iloc[:sidx].sum()

            fmt = {c: ("{:,.2f}" if any(kw in c for kw in ["단가","환율"]) else "{:,.0f}")
                   for c in num_cols_d}

            def row_style(row):
                if row.get("품목명","") == "【합 계】":
                    return ["font-weight:700"] * len(row)
                return [""] * len(row)

            st.dataframe(
                detail_df.style.format(fmt, na_rep="-").apply(row_style, axis=1),
                use_container_width=True, hide_index=True,
            )

    with tab_bar:
        va_bar     = va_filtered.set_index("품목명")["총차이"].sort_values()
        bar_colors = ["#e74c3c" if v < 0 else "#27ae60" for v in va_bar.values]
        bar_text   = [f"▼ {v:,.0f}" if v < 0 else (f"▲ +{v:,.0f}" if v > 0 else f"{v:,.0f}")
                      for v in va_bar.values]
        fig_bar = go.Figure(go.Bar(
            x=va_bar.values, y=va_bar.index, orientation="h",
            marker_color=bar_colors,
            marker_line=dict(color=["#b03a2e" if v<0 else "#1e8449" for v in va_bar.values], width=1),
            text=bar_text, textposition="outside",
            textfont=dict(size=12, color="#0d1f3c", family="Malgun Gothic, AppleGothic, sans-serif"),
        ))
        fig_bar.update_layout(
            title_text="품목별 총 매출 차이", title_font_size=14, title_x=0.01,
            height=max(380, len(va_bar)*40),
            margin=dict(l=10, r=140, t=50, b=30),
            plot_bgcolor="#fafbfd", paper_bgcolor="#ffffff",
            font=dict(family="Malgun Gothic, AppleGothic, sans-serif"),
            xaxis=dict(title="원화 매출 차이 (₩)", gridcolor="#e8ecf3",
                       zeroline=True, zerolinecolor="#5a6a85", zerolinewidth=2),
            yaxis=dict(tickfont=dict(size=12, color="#0d1f3c"), automargin=True),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

except ImportError:
    st.info("plotly가 설치되지 않아 차트를 표시할 수 없습니다.")

# ==============================================================================
# 다운로드
# ==============================================================================
st.markdown('<div class="section-header">⬇️ 결과 다운로드</div>', unsafe_allow_html=True)

def to_excel_bytes(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="차이분석")
    return buf.getvalue()

period_mode_label = "YoY" if "전년" in period_mode else "MoM"
model_label       = "A_원인별임팩트" if is_model_A else "B_활동별증분"
excel_bytes       = to_excel_bytes(va_disp_total.reset_index(drop=True))
st.download_button(
    label="📥 분석 결과 엑셀 다운로드",
    data=excel_bytes,
    file_name=f"매출차이분석_{model_label}_{period_mode_label}_{base_label}vs{curr_label}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

with st.expander("🗂️ 원본 데이터 확인 (선택 품목 기준)"):
    raw_base = df_base[df_base["품목명"].isin(selected_items)].reset_index(drop=True)
    raw_curr = df_curr[df_curr["품목명"].isin(selected_items)].reset_index(drop=True)
    t1, t2 = st.tabs([f"기준 ({base_label}) · {len(raw_base):,}건",
                       f"실적 ({curr_label}) · {len(raw_curr):,}건"])
    with t1:
        if not raw_base.empty:
            st.dataframe(raw_base, use_container_width=True, height=280)
        else:
            st.info("선택된 품목의 기준 기간 데이터가 없습니다.")
    with t2:
        if not raw_curr.empty:
            st.dataframe(raw_curr, use_container_width=True, height=280)
        else:
            st.info("선택된 품목의 실적 기간 데이터가 없습니다.")

# ==============================================================================
# 모델 상세 비교표
# ==============================================================================
render_model_guide()
