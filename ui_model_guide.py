# ==============================================================================
# ui_model_guide.py  --  분석 모델 상세 비교표 (다크 테마)
# ==============================================================================
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import streamlit as st


def render_model_guide():
    st.markdown('<div class="section-header">📖 분석 모델 상세 비교</div>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:rgba(124,58,237,0.10);border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:14px 18px;">
  <div style="font-size:0.62rem;font-weight:600;color:#7c3aed;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Model A</div>
  <div style="font-size:0.92rem;font-weight:600;color:#e2e8f0;margin-bottom:4px;">원인별 임팩트 분석</div>
  <div style="font-size:0.71rem;color:#475569;line-height:1.55;">변수 간 간섭을 제거해 각 요인의 <span style="color:#a78bfa;">절대적 영향력</span>을 측정. 재무·감사·외부보고 표준 모델.</div>
  <div style="margin-top:10px;padding:8px 10px;background:rgba(0,0,0,0.2);border-radius:8px;font-family:'SF Mono','Fira Code',monospace;font-size:0.67rem;color:#7c3aed;line-height:2.0;">
    ① (Q1-Q0) x P0_fx x ER0<br>② (P1-P0) x Q1 x ER0<br>③ (ER1-ER0) x Q1 x P1_fx
  </div>
</div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
<div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.25);border-radius:12px;padding:14px 18px;">
  <div style="font-size:0.62rem;font-weight:600;color:#f97316;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Model B</div>
  <div style="font-size:0.92rem;font-weight:600;color:#e2e8f0;margin-bottom:4px;">활동별 증분 분석</div>
  <div style="font-size:0.71rem;color:#475569;line-height:1.55;">영업 활동의 <span style="color:#fb923c;">실질적 비즈니스 가치</span>를 평가. 상황별 Case 가중치 적용.</div>
  <div style="margin-top:10px;padding:8px 10px;background:rgba(0,0,0,0.2);border-radius:8px;font-family:'SF Mono','Fira Code',monospace;font-size:0.67rem;color:#f97316;line-height:2.0;">
    ① Q up: (Q1-Q0)xP1_krw / Q dn: (Q1-Q0)xP0_krw<br>② 총차이 - ① - ③<br>③ P/Q 방향 4-Case
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ① 수량 차이
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #7c3aed;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#7c3aed;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">① Quantity Variance</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:7px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;margin-bottom:8px;">(Q실적 - Q기준) x P기준_fx x ER기준</div>
  <div style="font-size:0.71rem;color:#64748b;line-height:1.55;">수량·환율을 기준 고정. 수량 변화만의 순수 물량 효과.</div>
  <div style="font-size:0.62rem;color:#7c3aed;opacity:0.7;margin-top:5px;font-style:italic;">수량 증감 무관 — 항상 기준 외화단가 적용</div>
</div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #7c3aed;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#7c3aed;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">① Volume Incremental</div>
  <div style="font-size:0.62rem;color:#34d399;margin-bottom:2px;font-weight:500;">▲ 수량 증가 시</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:6px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;margin-bottom:6px;">(Q실적 - Q기준) x P실적_원화단가</div>
  <div style="font-size:0.62rem;color:#f87171;margin-bottom:2px;font-weight:500;">▼ 수량 감소 시</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:6px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;">(Q실적 - Q기준) x P기준_원화단가</div>
  <div style="font-size:0.71rem;color:#64748b;line-height:1.55;margin-top:7px;">새로 판 물건은 실적 가격으로, 잃은 물건은 기준 가격으로.</div>
</div>""", unsafe_allow_html=True)

    # ② 단가 차이
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #0ea5e9;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#0ea5e9;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">② Price Variance</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:7px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;margin-bottom:8px;">(P실적_fx - P기준_fx) x Q실적 x ER기준</div>
  <div style="font-size:0.71rem;color:#64748b;line-height:1.55;">수량은 실적 확정, 환율은 기준 고정. 외화 단가 변동의 순수 효과.</div>
  <div style="font-size:0.62rem;color:#0ea5e9;opacity:0.7;margin-top:5px;font-style:italic;">환율 기준 고정 → 환율 효과 완전 배제</div>
</div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #0ea5e9;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#0ea5e9;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">② Negotiation Residual</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:7px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;margin-bottom:8px;">총차이 - ①수량차이 - ③환율차이</div>
  <div style="font-size:0.71rem;color:#64748b;line-height:1.55;">수량·환율 효과를 제거하고 남은 단가 협상 결과. 잔여값(Residual)으로 항등식 보장.</div>
</div>""", unsafe_allow_html=True)

    # ③ 환율 차이
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #10b981;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#10b981;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">③ FX Variance</div>
  <div style="background:rgba(0,0,0,0.25);border-radius:6px;padding:7px 10px;font-family:'SF Mono','Fira Code',monospace;font-size:0.72rem;color:#e2e8f0;margin-bottom:8px;">(ER실적 - ER기준) x Q실적 x P실적_fx</div>
  <div style="font-size:0.71rem;color:#64748b;line-height:1.55;">수량·단가 실적 확정 후 환율 변동만으로 원화 환산액 변화 측정.</div>
  <div style="font-size:0.62rem;color:#10b981;opacity:0.7;margin-top:5px;font-style:italic;">KRW 거래는 환율차이 = 0</div>
</div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-left:3px solid #10b981;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:4px;">
  <div style="font-size:0.62rem;font-weight:600;color:#10b981;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">③ FX Exposure — 4-Case</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:8px;">
    <div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:5px 8px;">
      <div style="font-size:0.6rem;color:#10b981;font-weight:600;margin-bottom:2px;">단가↑ &amp; 수량↑</div>
      <div style="font-family:'SF Mono',monospace;font-size:0.63rem;color:#64748b;">dER x Q기 x P실_fx</div>
    </div>
    <div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:5px 8px;">
      <div style="font-size:0.6rem;color:#10b981;font-weight:600;margin-bottom:2px;">단가↑ &amp; 수량↓</div>
      <div style="font-family:'SF Mono',monospace;font-size:0.63rem;color:#64748b;">dER x Q실 x P실_fx</div>
    </div>
    <div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:5px 8px;">
      <div style="font-size:0.6rem;color:#10b981;font-weight:600;margin-bottom:2px;">단가↓ &amp; 수량↑</div>
      <div style="font-family:'SF Mono',monospace;font-size:0.63rem;color:#64748b;">dER x Q기 x P기_fx</div>
    </div>
    <div style="background:rgba(0,0,0,0.2);border-radius:5px;padding:5px 8px;">
      <div style="font-size:0.6rem;color:#10b981;font-weight:600;margin-bottom:2px;">단가↓ &amp; 수량↓</div>
      <div style="font-family:'SF Mono',monospace;font-size:0.63rem;color:#64748b;">dER x Q실 x P기_fx</div>
    </div>
  </div>
  <div style="font-size:0.71rem;color:#64748b;">단가/수량 방향 4조합에 따라 환율 노출 범위 적용.</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 비교 표
    st.markdown("""
<div style="font-size:0.62rem;font-weight:600;color:#7c3aed;letter-spacing:0.1em;text-transform:uppercase;padding:0 0 8px 10px;border-left:2px solid #7c3aed;margin-bottom:12px;">비교 요약</div>
<table style="width:100%;border-collapse:collapse;font-size:0.75rem;">
  <thead>
    <tr>
      <th style="padding:10px 14px;text-align:left;color:#475569;font-size:0.62rem;letter-spacing:0.08em;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.06);font-weight:600;">항목</th>
      <th style="padding:10px 14px;text-align:center;background:rgba(124,58,237,0.1);color:#a78bfa;font-size:0.72rem;font-weight:600;border-bottom:1px solid rgba(124,58,237,0.2);">모델 A</th>
      <th style="padding:10px 14px;text-align:center;background:rgba(249,115,22,0.08);color:#fb923c;font-size:0.72rem;font-weight:600;border-bottom:1px solid rgba(249,115,22,0.2);">모델 B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:9px 14px;color:#64748b;font-size:0.72rem;border-bottom:1px solid rgba(255,255,255,0.04);">수량↑ 시 단가 기준</td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(124,58,237,0.15);color:#a78bfa;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">기준 외화단가</span></td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(249,115,22,0.12);color:#fb923c;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">실적 원화단가</span></td>
    </tr>
    <tr>
      <td style="padding:9px 14px;color:#64748b;font-size:0.72rem;border-bottom:1px solid rgba(255,255,255,0.04);">단가차이 계산</td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(16,185,129,0.12);color:#34d399;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">직접 계산</span></td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(249,115,22,0.12);color:#fb923c;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">잔여값 Residual</span></td>
    </tr>
    <tr>
      <td style="padding:9px 14px;color:#64748b;font-size:0.72rem;border-bottom:1px solid rgba(255,255,255,0.04);">환율차이 계산</td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(16,185,129,0.12);color:#34d399;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">단일 공식</span></td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(249,115,22,0.12);color:#fb923c;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">4-Case 분기</span></td>
    </tr>
    <tr>
      <td style="padding:9px 14px;color:#64748b;font-size:0.72rem;border-bottom:1px solid rgba(255,255,255,0.04);">항등식 ①+②+③</td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(16,185,129,0.12);color:#34d399;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">수학적 항등</span></td>
      <td style="padding:9px 14px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);"><span style="background:rgba(16,185,129,0.12);color:#34d399;border-radius:4px;padding:2px 8px;font-size:0.68rem;font-weight:600;">설계상 보장</span></td>
    </tr>
    <tr>
      <td style="padding:9px 14px;color:#64748b;font-size:0.72rem;">적합한 보고</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:rgba(124,58,237,0.12);color:#a78bfa;border-radius:4px;padding:2px 7px;font-size:0.65rem;font-weight:600;margin:1px 2px;display:inline-block;">재무제표</span><span style="background:rgba(124,58,237,0.12);color:#a78bfa;border-radius:4px;padding:2px 7px;font-size:0.65rem;font-weight:600;margin:1px 2px;display:inline-block;">외부감사</span></td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:rgba(249,115,22,0.1);color:#fb923c;border-radius:4px;padding:2px 7px;font-size:0.65rem;font-weight:600;margin:1px 2px;display:inline-block;">영업성과</span><span style="background:rgba(249,115,22,0.1);color:#fb923c;border-radius:4px;padding:2px 7px;font-size:0.65rem;font-weight:600;margin:1px 2px;display:inline-block;">전략보고</span></td>
    </tr>
  </tbody>
</table>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
