# ==============================================================================
# ui_sidebar.py  —  사이드바 UI (파일 업로드, 기간 선택 등)
# ==============================================================================
# ⚠️ 이 파일은 스텁입니다. 실제 코드를 업로드해주세요.
# ==============================================================================
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import streamlit as st
import pandas as pd
from data_loader import load_excel


def render_sidebar() -> dict:
    """
    사이드바 UI를 렌더링하고 분석에 필요한 컨텍스트를 반환합니다.
    
    Returns:
        dict: {
            "df_all": pd.DataFrame,      # 전체 데이터
            "df_base": pd.DataFrame,     # 기준 기간 데이터
            "df_curr": pd.DataFrame,     # 실적 기간 데이터
            "base_label": str,           # 기준 기간 레이블
            "curr_label": str,           # 실적 기간 레이블
            "period_mode": str,          # 기간 모드
            "analysis_model": str,       # 분석 모델 (A 또는 B)
            "show_detail": bool,         # 상세 보기 여부
            "is_ytd": bool,              # YTD 여부
        }
    """
    with st.sidebar:
        st.markdown("### 📂 데이터 업로드")
        
        uploaded_file = st.file_uploader(
            "ERP 매출실적 파일 (.xlsx)",
            type=["xlsx", "xls"],
            key="erp_file"
        )
        
        df_all = None
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            df_all = load_excel(file_bytes, uploaded_file.name)
        
        st.markdown("---")
        st.markdown("### ⚙️ 분석 설정")
        
        period_mode = st.selectbox(
            "비교 기준",
            ["전년 동기", "전월", "계획"],
            key="period_mode"
        )
        
        analysis_model = st.radio(
            "분석 모델",
            ["A: 원인별 임팩트", "B: 활동별 증분"],
            key="analysis_model"
        )
        analysis_model = "A" if "A:" in analysis_model else "B"
        
        show_detail = st.checkbox("환종별 상세 보기", value=False, key="show_detail")
        
        # 기본값 설정
        df_base = pd.DataFrame()
        df_curr = pd.DataFrame()
        base_label = "기준"
        curr_label = "실적"
        is_ytd = False
        
        if df_all is not None and not df_all.empty:
            years = sorted(df_all["연도"].unique())
            months = sorted(df_all["월"].unique())
            
            if len(years) >= 1 and len(months) >= 1:
                curr_year = max(years)
                curr_month = max(months)
                
                df_curr = df_all[(df_all["연도"] == curr_year) & (df_all["월"] == curr_month)]
                curr_label = f"{curr_year}년 {curr_month}월"
                
                if period_mode == "전년 동기":
                    base_year = curr_year - 1
                    df_base = df_all[(df_all["연도"] == base_year) & (df_all["월"] == curr_month)]
                    base_label = f"{base_year}년 {curr_month}월"
                elif period_mode == "전월":
                    if curr_month > 1:
                        base_month = curr_month - 1
                        base_year = curr_year
                    else:
                        base_month = 12
                        base_year = curr_year - 1
                    df_base = df_all[(df_all["연도"] == base_year) & (df_all["월"] == base_month)]
                    base_label = f"{base_year}년 {base_month}월"
                else:
                    df_base = df_curr.copy()
                    base_label = "계획"
    
    return {
        "df_all": df_all,
        "df_base": df_base,
        "df_curr": df_curr,
        "base_label": base_label,
        "curr_label": curr_label,
        "period_mode": period_mode,
        "analysis_model": analysis_model,
        "show_detail": show_detail,
        "is_ytd": is_ytd,
    }
