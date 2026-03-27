# ==============================================================================
# ui_sidebar.py  —  사이드바 렌더링 (그룹 설정은 메인 화면으로 이동)
# ==============================================================================
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import streamlit as st
import pandas as pd
from io import BytesIO
from data_loader import load_excel
from config import MONTH_KR



def _parse_group_excel(data: bytes) -> dict:
    """그룹 설정 엑셀(품목명, 커스텀 그룹명) → {품목명: 그룹명} dict."""
    try:
        df = pd.read_excel(BytesIO(data), dtype=str).fillna("")
        if "품목명" not in df.columns or "커스텀 그룹명" not in df.columns:
            return {}
        return {
            str(row["품목명"]).strip(): str(row["커스텀 그룹명"]).strip()
            for _, row in df.iterrows()
            if str(row["품목명"]).strip() and str(row["커스텀 그룹명"]).strip()
        }
    except Exception:
        return {}


def render_sidebar():
    df_all = None

    with st.sidebar:
        st.markdown("#### 📂 파일 업로드")
        uploaded = st.file_uploader("ERP 매출실적 (.xlsx / .xls)", type=["xlsx", "xls"])



        if uploaded:
            df_all = load_excel(uploaded.read(), uploaded.name)

        if df_all is not None:
            st.markdown("### 📅 실적 연월")
            avail_years = sorted(df_all["연도"].unique())
            curr_year   = st.selectbox("실적 연도", avail_years, index=len(avail_years)-1)
            avail_m     = sorted(df_all[df_all["연도"] == curr_year]["월"].unique())
            curr_month  = st.selectbox("실적 월", avail_m,
                                       format_func=lambda x: MONTH_KR[x],
                                       index=len(avail_m)-1)

            st.markdown("### 🔀 비교 기간")
            period_mode = st.radio("기준 기간 설정",
                                   ["전년 동월 대비 (YoY)", "전월 대비 (MoM)", "전년 동기 누적 대비 (YTD)"], index=0)
            is_ytd = (period_mode == "전년 동기 누적 대비 (YTD)")

            if period_mode == "전년 동월 대비 (YoY)":
                base_year, base_month = curr_year - 1, curr_month
            elif period_mode == "전월 대비 (MoM)":
                base_year  = curr_year - 1 if curr_month == 1 else curr_year
                base_month = 12            if curr_month == 1 else curr_month - 1
            else:  # YTD
                base_year, base_month = curr_year - 1, curr_month

            if is_ytd:
                ytd_months = list(range(1, curr_month + 1))
                base_label = f"{base_year}년 1월~{curr_month}월 누적"
                curr_label = f"{curr_year}년 1월~{curr_month}월 누적"
            else:
                base_label = f"{base_year}년 {MONTH_KR[base_month]}"
                curr_label = f"{curr_year}년 {MONTH_KR[curr_month]}"

            st.markdown(
                f'<div style="margin-top:4px;">'
                f'<div style="display:inline-block;background:rgba(71,85,105,0.25);'
                f'color:#cbd5e1;border:1px solid rgba(100,116,139,0.4);border-radius:6px;'
                f'padding:3px 8px;font-size:0.72rem;font-weight:600;margin-bottom:3px;'
                f'white-space:normal;word-break:keep-all;">기준: {base_label}</div><br>'
                f'<div style="display:inline-block;background:rgba(124,58,237,0.2);'
                f'color:#c4b5fd;border:1px solid rgba(124,58,237,0.4);border-radius:6px;'
                f'padding:3px 8px;font-size:0.72rem;font-weight:600;margin-top:2px;'
                f'white-space:normal;word-break:keep-all;">실적: {curr_label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.markdown("### 🧮 분석 모델 선택")
            if "analysis_model" not in st.session_state:
                st.session_state.analysis_model = "모델 A — 원인별 임팩트 분석"
            is_A_active = "모델 A" in st.session_state.analysis_model
            _render_model_cards(is_A_active)
            analysis_model = st.session_state.analysis_model

            st.markdown("---")
            st.markdown("### ⚙️ 표시 설정")
            show_detail = st.checkbox("수량·단가·환율 상세 컬럼 표시", value=False)
            st.caption("ℹ️ ①수량차이 + ②단가차이 + ③환율차이 = 총차이")
            st.caption("🆕 신규 품목은 당해 매출 전액을 수량차이로 귀속 (단가·환율차이=0)")

            if is_ytd:
                df_base = df_all[(df_all["연도"] == base_year) & (df_all["월"].isin(ytd_months))].copy()
                df_curr = df_all[(df_all["연도"] == curr_year) & (df_all["월"].isin(ytd_months))].copy()
            else:
                df_base = df_all[(df_all["연도"] == base_year) & (df_all["월"] == base_month)].copy()
                df_curr = df_all[(df_all["연도"] == curr_year) & (df_all["월"] == curr_month)].copy()

        else:
            base_label = curr_label = period_mode = ""
            df_base = df_curr = None
            show_detail = False
            is_ytd = False
            if "analysis_model" not in st.session_state:
                st.session_state.analysis_model = "모델 A — 원인별 임팩트 분석"
            analysis_model = st.session_state.analysis_model

    return dict(
        df_all=df_all, df_base=df_base, df_curr=df_curr,
        base_label=base_label, curr_label=curr_label, period_mode=period_mode,
        analysis_model=analysis_model, show_detail=show_detail, is_ytd=is_ytd,
    )


def _render_model_cards(is_A_active: bool):
    if is_A_active:
        card_s = "background:rgba(124,58,237,0.18);border:1.5px solid rgba(124,58,237,0.5);border-radius:10px;padding:12px 14px;margin-bottom:4px;box-shadow:0 0 16px rgba(124,58,237,0.15);"
        title_s = "font-size:0.84rem;font-weight:600;color:#c4b5fd;"
        desc_s = "font-size:0.72rem;color:#8b5cf6;margin-top:4px;line-height:1.55;"
        tag_s = "display:inline-block;font-size:0.63rem;font-weight:600;border-radius:4px;padding:2px 8px;margin-top:6px;background:rgba(124,58,237,0.25);color:#a78bfa;border:1px solid rgba(124,58,237,0.4);"
        btn_lbl = "✔ 선택됨 (모델 A)"
    else:
        card_s = "background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 14px;margin-bottom:4px;"
        title_s = "font-size:0.84rem;font-weight:500;color:#64748b;"
        desc_s = "font-size:0.72rem;color:#475569;margin-top:4px;line-height:1.55;"
        tag_s = "display:inline-block;font-size:0.63rem;font-weight:500;border-radius:4px;padding:2px 8px;margin-top:6px;background:rgba(255,255,255,0.05);color:#64748b;border:1px solid rgba(255,255,255,0.1);"
        btn_lbl = "이 모델 선택 →"

    badge_a = '&nbsp;<span style="font-size:0.75rem;background:#27ae60;color:white;border-radius:3px;padding:1px 7px;">선택중</span>' if is_A_active else ''
    st.markdown(f"""
    <div style="{card_s}">
      <div style="{title_s}">📐 모델 A — 원인별 임팩트 분석{badge_a}</div>
      <div style="{desc_s}">
        변수 간 간섭을 완전히 제거하여<br>각 요인의 <b>절대적 영향력</b>을 측정.<br><br>
        ① 수량차이: (Q1−Q0)×<b>P0_fx</b>×<b>ER0</b><br>
        ② 단가차이: (P1−P0)×<b>Q1</b>×<b>ER0</b><br>
        ③ 환율차이: (ER1−ER0)×<b>Q1</b>×<b>P1_fx</b><br><br>
        <b>✔ 재무·감사·외부보고 표준</b>
      </div>
      <span style="{tag_s}">수량↑↓ 모두 전년 외화단가 적용</span>
    </div>""", unsafe_allow_html=True)
    if st.button(btn_lbl, key="sel_model_A", use_container_width=True,
                 type="primary" if is_A_active else "secondary"):
        st.session_state.analysis_model = "모델 A — 원인별 임팩트 분석"
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if not is_A_active:
        card_s = "background:rgba(249,115,22,0.12);border:1.5px solid rgba(249,115,22,0.4);border-radius:10px;padding:12px 14px;margin-bottom:4px;box-shadow:0 0 16px rgba(249,115,22,0.1);"
        title_s = "font-size:0.84rem;font-weight:600;color:#fdba74;"
        desc_s = "font-size:0.72rem;color:#f97316;margin-top:4px;line-height:1.55;"
        tag_s = "display:inline-block;font-size:0.63rem;font-weight:600;border-radius:4px;padding:2px 8px;margin-top:6px;background:rgba(249,115,22,0.2);color:#fb923c;border:1px solid rgba(249,115,22,0.35);"
        btn_lbl = "✔ 선택됨 (모델 B)"
    else:
        card_s = "background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 14px;margin-bottom:4px;"
        title_s = "font-size:0.84rem;font-weight:500;color:#64748b;"
        desc_s = "font-size:0.72rem;color:#475569;margin-top:4px;line-height:1.55;"
        tag_s = "display:inline-block;font-size:0.63rem;font-weight:500;border-radius:4px;padding:2px 8px;margin-top:6px;background:rgba(255,255,255,0.05);color:#64748b;border:1px solid rgba(255,255,255,0.1);"
        btn_lbl = "이 모델 선택 →"

    badge_b = '&nbsp;<span style="font-size:0.75rem;background:#27ae60;color:white;border-radius:3px;padding:1px 7px;">선택중</span>' if not is_A_active else ''
    st.markdown(f"""
    <div style="{card_s}">
      <div style="{title_s}">📈 모델 B — 활동별 증분 분석{badge_b}</div>
      <div style="{desc_s}">
        영업 활동의 <b>실질적 비즈니스 가치</b>를 평가.<br>
        상황(Case)에 따라 가중치를 다르게 적용.<br><br>
        ① 수량차이: Q↑→×<b>P1_krw</b> / Q↓→×<b>P0_krw</b><br>
        ② 단가차이: <b>총차이 − ① − ③</b> (잔여값)<br>
        ③ 환율차이: P/Q 방향 <b>4-Case 분기</b><br><br>
        <b>✔ 영업·전략·내부경영 보고</b>
      </div>
      <span style="{tag_s}">수량↑=현재 원화단가 / 수량↓=전년 원화단가</span>
    </div>""", unsafe_allow_html=True)
    if st.button(btn_lbl, key="sel_model_B", use_container_width=True,
                 type="primary" if not is_A_active else "secondary"):
        st.session_state.analysis_model = "모델 B — 활동별 증분 분석"
        st.rerun()
