# ==============================================================================
# ui_components.py  —  재사용 UI 컴포넌트 (KPI카드·테이블·Waterfall·Bar 차트)
# ==============================================================================
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)


import numpy as np
import pandas as pd
import streamlit as st


def styled_df(df: pd.DataFrame, money_cols: list):
    """지정 컬럼에 색상(양수=녹, 음수=적) 및 천단위 쉼표 포맷 적용."""
    def color_cell(v):
        try:
            fv = float(v)
            if fv < 0:   return "color:#f87171; font-weight:600"
            elif fv > 0: return "color:#34d399; font-weight:600"
        except Exception:
            pass
        return ""

    fmt_dict = {c: "{:,.0f}" for c in money_cols if c in df.columns}
    styler   = df.style.format(fmt_dict, na_rep="-")
    for c in money_cols:
        if c in df.columns:
            styler = styler.applymap(color_cell, subset=[c])
    return styler


def kpi_card(col, label: str, formula: str, value: float, neutral: bool = False):
    """단일 KPI 카드 렌더링 (미니멀 플랫 디자인)."""
    sign = "+" if value > 0 else ""
    if neutral:
        card_cls, val_cls = "kpi-card-neutral", "kpi-val-neutral"
        trend = ""
    elif value > 0:
        card_cls, val_cls = "kpi-card-pos", "kpi-val-pos"
        trend = '<span style="font-size:0.68rem;font-weight:600;color:#10b981;background:#f0fdf4;border-radius:4px;padding:1px 6px;margin-left:6px;">▲</span>'
    elif value < 0:
        card_cls, val_cls = "kpi-card-neg", "kpi-val-neg"
        trend = '<span style="font-size:0.68rem;font-weight:600;color:#f43f5e;background:#fff1f2;border-radius:4px;padding:1px 6px;margin-left:6px;">▼</span>'
    else:
        card_cls, val_cls = "kpi-card-zero", "kpi-val-zero"
        trend = ""

    col.markdown(f"""
    <div class="kpi-card {card_cls}">
        <div class="kpi-label">{label}{trend}</div>
        <div class="kpi-formula">{formula}</div>
        <div class="kpi-value {val_cls}">{sign}{value:,.0f}<span style="font-size:0.8rem;font-weight:400;color:inherit;opacity:0.6;margin-left:3px;">원</span></div>
    </div>""", unsafe_allow_html=True)


def render_waterfall(
    total_base: float, qty_v: float, price_v: float, fx_v: float,
    total_curr: float, base_label: str, curr_label: str, accent: str,
    unit: str = "백만원",
):
    """Waterfall 차트 반환. unit: 백만원 or 원"""
    import plotly.graph_objects as go

    CLR_BASE = "#6366f1"
    CLR_CURR = "#38bdf8"
    CLR_UP   = "#34d399"
    CLR_DOWN = "#f87171"
    CLR_CONN = "rgba(124,58,237,0.4)"

    use_M = (unit == "백만원")
    DIV   = 1_000_000 if use_M else 1
    sfx   = ""  # Y축 suffix 없이 숫자만 표시

    def bar_color(v): return CLR_UP if v >= 0 else CLR_DOWN
    def fmt_diff(v):
        mv = v / DIV
        fmt = f"{mv:,.1f}" if use_M else f"{mv:,.0f}"
        if v > 0: return f"▲ +{fmt}"
        if v < 0: return f"▼ {fmt}"
        return fmt

    x_labels   = [f"<b>기준 매출</b><br><sub>({base_label})</sub>",
                  "<b>① 수량 차이</b>", "<b>② 단가 차이</b>", "<b>③ 환율 차이</b>",
                  f"<b>실적 매출</b><br><sub>({curr_label})</sub>"]

    _b = total_base / DIV; _q = qty_v / DIV; _p = price_v / DIV
    _f = fx_v / DIV;       _c = total_curr / DIV

    text_labels = [
        f"{_b:,.1f}" if use_M else f"{_b:,.0f}",
        fmt_diff(qty_v), fmt_diff(price_v), fmt_diff(fx_v),
        f"{_c:,.1f}" if use_M else f"{_c:,.0f}",
    ]

    running   = [0, _b, _b+_q, _b+_q+_p]
    bar_vals  = [_b, _q, _p, _f, _c]
    bar_bases = [0, running[1], running[2], running[3], 0]
    bar_clrs  = [CLR_BASE, bar_color(qty_v), bar_color(price_v), bar_color(fx_v), CLR_CURR]
    line_clrs = ["#1e4080",
                 "#1e8449" if qty_v  >=0 else "#b03a2e",
                 "#1e8449" if price_v>=0 else "#b03a2e",
                 "#1e8449" if fx_v   >=0 else "#b03a2e",
                 "#145a32"]

    fig = go.Figure()
    for i, (x, y, base, clr, lclr, txt) in enumerate(
        zip(x_labels, bar_vals, bar_bases, bar_clrs, line_clrs, text_labels)
    ):
        fig.add_trace(go.Bar(
            name="", x=[x], y=[y], base=[0 if i == 4 else base],
            marker_color=clr, marker_line=dict(color=lclr, width=1.5),
            text=[txt], textposition="outside",
            textfont=dict(size=12, color="#e2e8f0", family="Inter, Noto Sans KR, sans-serif"),
            showlegend=False, width=0.55,
        ))

    connector_y = [_b, _b+_q, _b+_q+_p, _b+_q+_p+_f]
    for i, cy in enumerate(connector_y):
        fig.add_shape(type="line", x0=i+0.28, x1=i+0.72, y0=cy, y1=cy,
                      line=dict(color=CLR_CONN, width=1.5, dash="dot"))

    diff_val  = total_curr - total_base
    diff_sign = "▲ +" if diff_val >= 0 else "▼ "
    diff_pct  = f"({diff_val/total_base*100:+.1f}%)" if total_base != 0 else ""
    diff_d    = diff_val / DIV
    diff_fmt  = f"{diff_d:,.1f}" if use_M else f"{diff_d:,.0f}"
    unit_lbl  = "백만원" if use_M else "원"
    fig.update_layout(
        title_text=f"{base_label} → {curr_label}  ·  총차이 {diff_sign}{diff_fmt}{unit_lbl} {diff_pct}",
        title_font=dict(size=13, color="#94a3b8", family="Inter, Noto Sans KR, sans-serif"),
        title_x=0.01,
        barmode="stack",
        height=460,
        margin=dict(t=60, b=40, l=50, r=50),
        plot_bgcolor="#0d0d1f",
        paper_bgcolor="#0d0d1f",
        showlegend=False,
        font=dict(family="Inter, Noto Sans KR, sans-serif", size=12, color="#94a3b8"),
        xaxis=dict(
            tickfont=dict(size=11, color="#64748b", family="Inter, sans-serif"),
            tickangle=0,
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=f"({unit_lbl})" if use_M else "(원)",
            title_font=dict(size=10, color="#475569"),
            tickfont=dict(size=10, color="#475569", family="Inter, sans-serif"),
            tickformat=",",
            gridcolor="rgba(124,58,237,0.15)",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="rgba(124,58,237,0.3)",
            zerolinewidth=1,
            showline=False,
        ),
    )
    return fig


def build_table(
    df_in: pd.DataFrame, base_label: str, curr_label: str, show_detail: bool
):
    """
    품목별 차이 분석 테이블 생성.
    show_detail=False: 품목명 단위 합산 뷰 (환종 컬럼 없음)
    show_detail=True : 환종별 분리 뷰 (단가·환율 컬럼 포함)

    반환: (표시용 DataFrame, money_cols 리스트)
    """
    display_cols = ["품목명","is_krw","Q0","매출0","매출1","총차이","수량차이","단가차이","환율차이"]
    if show_detail:
        if "환종" in df_in.columns:
            display_cols = ["품목명","환종","is_krw","Q0"] + display_cols[3:]
        extra = [c for c in ["Q1","P0_fx","P1_fx","P0_krw","P1_krw","ER0","ER1"]
                 if c in df_in.columns]
        display_cols += [c for c in extra if c not in display_cols]

    va_d = df_in[[c for c in display_cols if c in df_in.columns]].copy()
    va_d = va_d.sort_values("총차이").reset_index(drop=True)

    is_new = va_d["Q0"] == 0
    va_d.loc[is_new, "품목명"] = "🆕 " + va_d.loc[is_new, "품목명"].astype(str)

    if not show_detail:
        va_d = va_d.drop(columns=["Q0"], errors="ignore")

    if "is_krw" in va_d.columns:
        krw_mask = va_d["is_krw"] == True
        for fx_col in ["P0_fx","P1_fx","ER0","ER1","환율차이"]:
            if fx_col in va_d.columns:
                va_d.loc[krw_mask, fx_col] = np.nan
    va_d = va_d.drop(columns=["is_krw"], errors="ignore")

    rename_map = {
        "매출0": f"기준매출(원) [{base_label}]",
        "매출1": f"실적매출(원) [{curr_label}]",
        "총차이":   "총차이(원)",
        "수량차이": "①수량차이(원)",
        "단가차이": "②단가차이(원)",
        "환율차이": "③환율차이(원)",
        "Q0":"기준수량","Q1":"실적수량",
        "P0_fx":"기준외화단가","P1_fx":"실적외화단가",
        "P0_krw":"기준원화단가","P1_krw":"실적원화단가",
        "ER0":"기준환율","ER1":"실적환율",
    }
    va_d = va_d.rename(columns=rename_map)

    money_cols  = [f"기준매출(원) [{base_label}]", f"실적매출(원) [{curr_label}]",
                   "총차이(원)","①수량차이(원)","②단가차이(원)","③환율차이(원)"]
    sum_targets = money_cols + (["기준수량","실적수량"] if "기준수량" in va_d.columns else [])

    total_row = {}
    for col in va_d.columns:
        if col in sum_targets:   total_row[col] = va_d[col].sum(skipna=True)
        elif col == "품목명":    total_row[col] = "【 합 계 】"
        else:                    total_row[col] = ""

    return pd.concat([va_d, pd.DataFrame([total_row])], ignore_index=True), money_cols
