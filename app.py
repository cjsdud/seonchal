
import streamlit as st, pandas as pd, numpy as np, joblib, plotly.express as px

st.set_page_config(page_title="선찰(先察)", page_icon="🔍", layout="wide")

@st.cache_resource
def load():
    return joblib.load("model.pkl"), joblib.load("lookups.pkl"), pd.read_csv("data.csv", low_memory=False)
MODEL, L, D = load()
HI, MID = 0.50, 0.30
GRADE_STAT = {"고위험": 78.0, "주의": 47.5, "양호": 15.9}

def predict(기관명, 품목명, 업무, 계약방법, 제조제한, 긴급, 업종제한, 재공고):
    row = dict(L["cat_def"]); row.update(L["num_def"])
    oc = L["org_map"].get(기관명); ic = L["item_map"].get(품목명)
    row["수요기관코드"] = oc if oc in L["cats"]["수요기관코드"] else L["cat_def"]["수요기관코드"]
    row["품목대분류2"]  = ic if ic in L["cats"]["품목대분류2"] else L["cat_def"]["품목대분류2"]
    row["업무구분"] = 업무; row["계약방법"] = 계약방법
    row["제조물품제한여부"] = 제조제한; row["긴급공고여부"] = 긴급; row["업종제한여부"] = 업종제한
    ir = L["lk_item"].get(ic, {"rate": L["base"], "n": 0})
    orr = L["lk_org"].get(oc, {"rate": L["base"], "n": 0})
    row["과거_대분류"]=ir["rate"]; row["과거_대분류_n"]=ir["n"]
    row["과거_중분류"]=ir["rate"]; row["과거_품명"]=ir["rate"]
    row["과거_기관"]=orr["rate"]; row["과거_기관_n"]=orr["n"]
    row["과거_기관품목"]=0.5*orr["rate"]+0.5*ir["rate"]
    row["재공고"] = 1 if 재공고 else 0
    row["차수"]   = 1 if 재공고 else 0
    x = pd.DataFrame([row])
    for c in L["CAT"]:
        x[c] = pd.Categorical([str(x[c].iloc[0])], categories=L["cats"][c])
    for c in L["NUM"]: x[c] = pd.to_numeric(x[c], errors="coerce")
    return float(MODEL.predict_proba(x[L["CAT"]+L["NUM"]])[:,1][0])

st.title("🔍 선찰(先察) — 국방 조달 무응찰 조기경보")
st.caption("2020~2025 국방 발주 12,641건 분석 · 유찰의 92.7%는 응찰자 0명 · 모델 ROC-AUC 0.806")

t1,t2,t3,t4 = st.tabs(["📊 공급취약도 지도","⚠️ 공고 사전진단","🔁 재공고 경보","📈 품목 상세"])

with t1:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("전체 유찰률", f"{D['유찰'].mean():.1%}")
    c2.metric("유찰 중 무응찰", "92.7%")
    c3.metric("공급두께–유찰 상관", "-0.729")
    c4.metric("5년 추세", "변화 없음", help="기울기 +0.01%p/년, p=0.99 — 만성적 구조")
    g = D.dropna(subset=["품목대분류"]).groupby("품목대분류").agg(
        건수=("유찰","size"), 유찰률=("유찰","mean"), 중앙응찰=("응찰수","median")).reset_index()
    g = g[g["건수"]>=25]
    fig = px.scatter(g, x="중앙응찰", y="유찰률", size="건수", text="품목대분류", color="유찰률",
                     color_continuous_scale="Reds",
                     labels={"중앙응찰":"중앙 응찰자수 (공급 두께)","유찰률":"유찰률"},
                     title="공급이 얇을수록 유찰이 잦다")
    fig.update_traces(textposition="top center"); fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(g.sort_values("유찰률", ascending=False).style.format(
        {"유찰률":"{:.1%}","중앙응찰":"{:.0f}"}), use_container_width=True, height=320)

with t2:
    st.subheader("공고를 내기 전에 진단합니다")
    c1,c2 = st.columns(2)
    with c1:
        기관 = st.selectbox("수요기관", sorted(L["org_map"].keys()))
        품목 = st.selectbox("품목 대분류", sorted(L["item_map"].keys()))
        업무 = st.selectbox("업무구분", L["cats"]["업무구분"])
        계약 = st.selectbox("계약방법", L["cats"]["계약방법"])
    with c2:
        제조 = st.radio("제조물품제한", ["N","Y"], horizontal=True,
                      help="직접 제조업체로 한정. 통계상 유찰률 +24.3%p (21개 품목 중 19개 일관)")
        업종 = st.radio("업종제한", ["N","Y"], horizontal=True)
        긴급 = st.radio("긴급공고", ["N","Y"], horizontal=True)
        재공 = st.checkbox("재공고 건")
        st.caption("※ 공고기간은 통계적 효과가 확인되지 않아 조정 항목에서 제외했습니다.")
    if st.button("진단하기", type="primary", use_container_width=True):
        p = predict(기관, 품목, 업무, 계약, 제조, 긴급, 업종, 재공)
        lv = "고위험" if p>=HI else ("주의" if p>=MID else "양호")
        icon = {"고위험":"🔴","주의":"🟡","양호":"🟢"}[lv]
        st.markdown(f"## {icon} {lv}")
        st.progress(min(p,1.0))
        st.info(f"이 등급을 받은 과거 공고의 **{GRADE_STAT[lv]}%**가 실제로 응찰자 0명이었습니다.")
        if lv=="고위험":
            st.error("**권고** · 사전 시장조사 → 공급 가능 업체 확인\n\n"
                     "· 수요통합 검토 (소량 분할 발주 지양)\n\n· 일정 버퍼 확보\n\n· 수의전환 절차 사전 준비")
        elif lv=="주의":
            st.warning("**권고** · 제조물품제한 필요성 재검토\n\n· 유사 과거공고 응찰이력 확인")
        else:
            st.success("통상 절차로 진행 가능합니다.")
        if 제조=="Y":
            st.caption("💡 제조물품제한을 해제하면 위험도가 낮아질 수 있습니다 (품목별 평균 -24.3%p).")
        s = D[(D["수요기관"]==기관)&(D["품목대분류"]==품목)]
        if len(s):
            st.markdown(f"**참고: {기관} · {품목} 과거 {len(s)}건** — "
                        f"무응찰률 {s['무응찰'].mean():.1%}, 중앙 응찰 {s['응찰수'].median():.0f}명")
            st.dataframe(s[["공고일자","공고명","응찰수","입찰진행상태값"]].tail(8),
                         use_container_width=True, hide_index=True)

with t3:
    st.subheader("재공고는 회복 수단이 아니다")
    r = D.groupby("공고상태값").agg(건수=("유찰","size"), 유찰률=("유찰","mean")).reset_index()
    r = r[r["건수"]>=50]
    st.plotly_chart(px.bar(r, x="공고상태값", y="유찰률", text_auto=".1%", color="유찰률",
                           color_continuous_scale="Reds", title="재공고 유찰률 59.7% — 등록공고의 2.8배"),
                    use_container_width=True)
    st.warning("**같은 조건으로 다시 내걸면 절반 이상이 또 무응찰입니다.** "
               "재공고에 앞서 수요통합 · 규격 재검토 · 수의전환을 우선 고려하십시오.")
    rep = D[D["공고상태값"]=="재공고"].dropna(subset=["품목대분류"])
    t = rep.groupby("품목대분류").agg(재공고건수=("유찰","size"), 재유찰률=("유찰","mean"))
    st.dataframe(t[t["재공고건수"]>=10].sort_values("재유찰률", ascending=False)
                 .style.format({"재유찰률":"{:.1%}"}), use_container_width=True)

with t4:
    p4 = st.selectbox("품목 선택", sorted(D["품목대분류"].dropna().unique()))
    s = D[D["품목대분류"]==p4]
    c = st.columns(4)
    c[0].metric("건수", f"{len(s):,}")
    c[1].metric("유찰률", f"{s['유찰'].mean():.1%}")
    c[2].metric("무응찰률", f"{s['무응찰'].mean():.1%}")
    c[3].metric("중앙 응찰자수", f"{s['응찰수'].median():.0f}명")
    yr = s.groupby("연도").agg(유찰률=("유찰","mean")).reset_index()
    f = px.line(yr, x="연도", y="유찰률", markers=True, title=f"{p4} 연도별 유찰률")
    f.update_yaxes(tickformat=".0%"); st.plotly_chart(f, use_container_width=True)
    o = s.groupby("수요기관").agg(건수=("유찰","size"), 유찰률=("유찰","mean"))
    st.dataframe(o[o["건수"]>=10].sort_values("유찰률", ascending=False)
                 .style.format({"유찰률":"{:.1%}"}), use_container_width=True)

st.caption("데이터: 조달정보개방포털 입찰공고 내역(2020~2025, 국방부 하위기관 포함) · "
           "학습 2020–23 / 검증 2024 / 테스트 2025 시간분할")
