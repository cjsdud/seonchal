import streamlit as st, pandas as pd, numpy as np, joblib, plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="선찰 先察", page_icon="◧", layout="wide",
                   initial_sidebar_state="collapsed")

INK, PAPER, RULE = "#16202C", "#F5F6F4", "#C9CDD2"
SEAL, STEEL, SLATE = "#B4232A", "#3E5C76", "#5A6672"

st.markdown("""<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=Noto+Serif+KR:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet"><style>:root { --ink:#16202C; --paper:#F5F6F4; --rule:#C9CDD2; --seal:#B4232A; --steel:#3E5C76; --slate:#5A6672; } html, body, [class*="css"], .stApp { font-family:'IBM Plex Sans KR',sans-serif; background:var(--paper); color:var(--ink); } .block-container { padding:2.2rem 3rem 4rem; max-width:1180px; } #MainMenu, footer, header { visibility:hidden; } .doc-head { border-top:2.5px solid var(--ink); padding-top:.9rem; margin-bottom:1.8rem; } .doc-meta { display:flex; justify-content:space-between; align-items:baseline; font-family:'IBM Plex Mono',monospace; font-size:.70rem; letter-spacing:.09em; color:var(--slate); text-transform:uppercase; margin-bottom:1rem; } .doc-title { font-family:'Noto Serif KR',serif; font-weight:700; font-size:2.85rem; line-height:1.12; letter-spacing:-.02em; margin:0; } .doc-title .han { color:var(--seal); font-weight:600; margin-left:.35rem; font-size:2.1rem; } .doc-sub { font-size:1.02rem; color:var(--slate); margin-top:.7rem; font-weight:300; line-height:1.65; max-width:62ch; } .doc-sub b { color:var(--ink); font-weight:600; } .flow { border:1px solid var(--rule); background:#fff; padding:1.3rem 1.5rem 1.1rem; margin:1.6rem 0 1.2rem; } .flow-h { font-size:.72rem; letter-spacing:.09em; color:var(--slate); margin-bottom:1rem; font-family:'IBM Plex Mono',monospace; } .flow-row { display:flex; align-items:stretch; flex-wrap:wrap; } .fstep { flex:1; min-width:135px; padding:0 1rem; border-left:1px solid var(--rule); } .fstep:first-child { border-left:none; padding-left:0; } .fs-n { font-family:'IBM Plex Mono',monospace; font-size:.66rem; color:var(--seal); letter-spacing:.1em; } .fs-t { font-family:'Noto Serif KR',serif; font-size:1.05rem; font-weight:600; margin:.25rem 0 .3rem; } .fs-d { font-size:.79rem; color:var(--slate); line-height:1.55; font-weight:300; } .fstep.fail .fs-t { color:var(--seal); } .fstep.fail { background:rgba(180,35,42,.04); } .flow-note { margin-top:1rem; padding-top:.85rem; border-top:1px dashed var(--rule); font-size:.83rem; color:var(--slate); line-height:1.7; } .flow-note b { color:var(--ink); } .ledger { display:grid; grid-template-columns:repeat(4,1fr); border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); margin:1.6rem 0 1.4rem; } .ledger div { padding:1.05rem 1.3rem; border-right:1px solid var(--rule); } .ledger div:last-child { border-right:none; } .lg-k { font-size:.72rem; letter-spacing:.05em; color:var(--slate); margin-bottom:.42rem; } .lg-v { font-family:'IBM Plex Mono',monospace; font-size:1.85rem; font-weight:600; line-height:1; letter-spacing:-.02em; } .lg-v.sig { color:var(--seal); } .lg-n { font-size:.70rem; color:var(--slate); margin-top:.38rem; font-weight:300; line-height:1.45; } .sec { margin:2.6rem 0 1rem; padding-bottom:.55rem; border-bottom:1px solid var(--rule); } .sec-n { font-family:'IBM Plex Mono',monospace; font-size:.68rem; letter-spacing:.14em; color:var(--seal); display:block; margin-bottom:.3rem; } .sec-t { font-family:'Noto Serif KR',serif; font-size:1.32rem; font-weight:600; } .sec-d { font-size:.87rem; color:var(--slate); margin-top:.4rem; font-weight:300; line-height:1.6; } .howto { background:#fff; border:1px solid var(--rule); border-left:3px solid var(--steel); padding:.85rem 1.1rem; margin:.9rem 0 1.2rem; font-size:.83rem; line-height:1.75; color:var(--slate); } .howto b.h { color:var(--ink); display:block; font-size:.71rem; letter-spacing:.08em; margin-bottom:.35rem; font-family:'IBM Plex Mono',monospace; } .tally { display:flex; align-items:flex-end; gap:.62rem; height:34px; margin:.5rem 0; } .tgrp { display:flex; gap:3px; } .tick { width:2.5px; height:26px; background:var(--ink); display:block; } .tick.x { transform:rotate(24deg); transform-origin:bottom; margin-left:-13px; } .tally-none { font-family:'Noto Serif KR',serif; font-size:1.25rem; color:var(--seal); border:1.5px solid var(--seal); padding:.22rem 1rem; letter-spacing:.35em; } .tally-cap { font-family:'IBM Plex Mono',monospace; font-size:.74rem; color:var(--slate); margin-left:.5rem; align-self:center; } .verdict { border:1.5px solid var(--ink); padding:1.5rem 1.7rem; margin:.4rem 0 1rem; background:#fff; } .verdict.hi { border-color:var(--seal); } .v-grade { font-family:'Noto Serif KR',serif; font-size:2rem; font-weight:700; line-height:1; margin-bottom:.55rem; } .v-grade.hi { color:var(--seal); } .v-fact { font-size:.94rem; line-height:1.6; } .v-fact b { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; } .v-act { margin-top:1rem; padding-top:.9rem; border-top:1px dashed var(--rule); font-size:.87rem; line-height:1.85; color:var(--slate); } .v-act b { color:var(--ink); display:block; margin-bottom:.35rem; font-size:.72rem; letter-spacing:.08em; } .grades { display:grid; grid-template-columns:repeat(3,1fr); border:1px solid var(--rule); background:#fff; margin:1rem 0; } .gr { padding:.9rem 1.1rem; border-right:1px solid var(--rule); } .gr:last-child { border-right:none; } .gr-n { font-family:'Noto Serif KR',serif; font-weight:700; font-size:1.05rem; } .gr-n.hi { color:var(--seal); } .gr-d { font-size:.76rem; color:var(--slate); margin-top:.35rem; line-height:1.5; } .gr-v { font-family:'IBM Plex Mono',monospace; font-size:1.3rem; font-weight:600; margin-top:.5rem; } .stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:1px solid var(--rule); } .stTabs [data-baseweb="tab"] { height:auto; padding:.72rem 1.4rem; background:transparent; border:none; border-bottom:2px solid transparent; font-size:.90rem; font-weight:500; color:var(--slate); } .stTabs [aria-selected="true"] { color:var(--ink); border-bottom-color:var(--seal); } .stTabs [data-baseweb="tab-panel"] { padding-top:1.6rem; } .stSelectbox label, .stRadio label, .stCheckbox label { font-size:.80rem !important; font-weight:500 !important; color:var(--slate) !important; } .stButton>button { background:var(--ink); color:var(--paper); border:none; border-radius:0; font-weight:600; font-size:.92rem; padding:.72rem 0; letter-spacing:.04em; } .stButton>button:hover { background:var(--seal); color:#fff; } .stButton>button:focus-visible { outline:2px solid var(--seal); outline-offset:2px; } [data-testid="stExpander"] { border:1px solid var(--rule); background:#fff; } [data-testid="stExpander"] summary { font-size:.85rem !important; font-weight:500 !important; } .stDataFrame { border:1px solid var(--rule); } .stDataFrame td, .stDataFrame th { font-size:.84rem !important; } .note { font-size:.79rem; color:var(--slate); line-height:1.75; font-weight:300; border-left:2px solid var(--rule); padding-left:.85rem; margin:1rem 0; } .note b { color:var(--ink); font-weight:600; } .foot { margin-top:3.5rem; padding-top:1.1rem; border-top:1px solid var(--rule); font-family:'IBM Plex Mono',monospace; font-size:.70rem; color:var(--slate); line-height:1.8; } .gloss { display:grid; grid-template-columns:repeat(2,1fr); gap:0 2rem; } .gi { padding:.7rem 0; border-bottom:1px solid var(--rule); } .gi-t { font-weight:600; font-size:.88rem; } .gi-d { font-size:.81rem; color:var(--slate); line-height:1.6; margin-top:.22rem; font-weight:300; } @media (max-width:820px) { .block-container { padding:1.4rem 1.1rem 3rem; } .doc-title { font-size:2rem; } .ledger, .grades, .gloss { grid-template-columns:repeat(2,1fr); } .ledger div, .gr { border-bottom:1px solid var(--rule); } .fstep { min-width:50%; border-left:none; padding:.6rem 0; } } @media (prefers-reduced-motion:reduce) { * { transition:none !important; } }.meter-wrap{margin:.9rem 0 .2rem;} .meter{position:relative;height:13px;background:linear-gradient(90deg,#3E5C76 0%,#3E5C76 30%,#8A93A0 30%,#8A93A0 50%,#B4232A 50%,#B4232A 100%);opacity:.92;} .meter-pin{position:absolute;top:-5px;width:3px;height:23px;background:#16202C;box-shadow:0 0 0 1.5px #F5F6F4;} .meter-lab{position:relative;height:15px;font-family:'IBM Plex Mono',monospace;font-size:.66rem;color:#5A6672;margin-top:.3rem;} .meter-lab span{position:absolute;top:0;white-space:nowrap;} .meter-lab .l30{left:30%;} .meter-lab .l50{left:50%;color:#B4232A;} .meter-lab .l100{right:0;} .score-line{display:flex;align-items:baseline;gap:.6rem;margin:.2rem 0 .4rem;} .score-v{font-family:'IBM Plex Mono',monospace;font-size:1.6rem;font-weight:600;} .score-c{font-size:.74rem;color:#5A6672;} .basis{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid #C9CDD2;background:#fff;margin:.7rem 0 .3rem;} .bi{padding:.7rem .95rem;border-right:1px solid #C9CDD2;} .bi:last-child{border-right:none;} .bi-k{font-size:.68rem;color:#5A6672;margin-bottom:.3rem;} .bi-v{font-family:'IBM Plex Mono',monospace;font-size:1.2rem;font-weight:600;} .bi-n{font-size:.66rem;color:#5A6672;margin-top:.25rem;}</style>""", unsafe_allow_html=True)

PLOT = go.layout.Template(layout=dict(
    font=dict(family="IBM Plex Sans KR, sans-serif", size=12, color=INK),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="#E3E5E4", linecolor=RULE, zerolinecolor=RULE, ticks="outside",
               tickcolor=RULE, ticklen=4),
    yaxis=dict(gridcolor="#E3E5E4", linecolor=RULE, zerolinecolor=RULE),
    margin=dict(t=28, b=48, l=52, r=20), hoverlabel=dict(font_size=12)))


@st.cache_resource
def load():
    return (joblib.load("model.pkl"), joblib.load("lookups.pkl"),
            pd.read_csv("data.csv", low_memory=False))
MODEL, L, D = load()
HI, MID = 0.50, 0.30
STAT = {"고위험": 78.0, "주의": 47.5, "양호": 15.9}


def tally(n):
    if pd.isna(n):
        return '<div class="tally"><span class="tally-cap">기록 없음</span></div>'
    n = int(n)
    if n == 0:
        return ('<div class="tally"><span class="tally-none">응찰 없음</span>'
                '<span class="tally-cap">0곳</span></div>')
    shown, groups = min(n, 20), []
    for i in range(0, shown, 5):
        k = min(5, shown - i)
        ticks = "".join(f'<span class="tick{" x" if j == 4 else ""}"></span>' for j in range(k))
        groups.append(f'<span class="tgrp">{ticks}</span>')
    more = f'<span class="tally-cap">외 {n-20}곳</span>' if n > 20 else ""
    return (f'<div class="tally">{"".join(groups)}'
            f'<span class="tally-cap">{n}곳</span>{more}</div>')


def predict(org, item, biz, method, mfr, urgent, ind, re_notice):
    row = dict(L["cat_def"]); row.update(L["num_def"])
    oc, ic = L["org_map"].get(org), L["item_map"].get(item)
    row["수요기관코드"] = oc if oc in L["cats"]["수요기관코드"] else L["cat_def"]["수요기관코드"]
    row["품목대분류2"] = ic if ic in L["cats"]["품목대분류2"] else L["cat_def"]["품목대분류2"]
    row.update({"업무구분": biz, "계약방법": method, "제조물품제한여부": mfr,
                "긴급공고여부": urgent, "업종제한여부": ind})
    ir = dict(L["lk_item"].get(ic, {"rate": L["base"], "n": 0}))
    orr = dict(L["lk_org"].get(oc, {"rate": L["base"], "n": 0})) if oc else {"rate": L["base"], "n": 0}
    row.update({"과거_대분류": ir["rate"], "과거_대분류_n": ir["n"],
                "과거_중분류": ir["rate"], "과거_품명": ir["rate"],
                "과거_기관": orr["rate"], "과거_기관_n": orr["n"],
                "과거_기관품목": .5 * orr["rate"] + .5 * ir["rate"],
                "재공고": int(re_notice), "차수": int(re_notice)})
    x = pd.DataFrame([row])
    for c in L["CAT"]:
        x[c] = pd.Categorical([str(x[c].iloc[0])], categories=L["cats"][c])
    for c in L["NUM"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    p = float(MODEL.predict_proba(x[L["CAT"] + L["NUM"]])[:, 1][0])
    return p, ir, orr


def sec(num, title, desc=""):
    st.markdown(f'<div class="sec"><span class="sec-n">{num}</span>'
                f'<span class="sec-t">{title}</span>'
                + (f'<div class="sec-d">{desc}</div>' if desc else "") + '</div>',
                unsafe_allow_html=True)


def howto(title, body):
    st.markdown(f'<div class="howto"><b class="h">{title}</b>{body}</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
st.markdown("""<div class="doc-head"><div class="doc-meta"><span>국방 조달 무응찰 조기경보</span><span>2020 — 2025 · 12,641건 · ROC-AUC 0.806</span></div><h1 class="doc-title">선찰<span class="han">先察</span></h1><p class="doc-sub">군이 물건을 사려고 공고를 냅니다. 그런데 <b>4건 중 1건은 아무도 오지 않습니다.</b> 유찰의 92.7%는 경쟁이 부족했던 것이 아니라, 응찰한 업체가 한 곳도 없었던 경우입니다. 선찰은 공고를 게시하기 전에 그 위험을 알려드립니다.</p></div><div class="flow"><div class="flow-h">군은 이렇게 물건을 삽니다 — 그리고 어디서 문제가 생기는가</div><div class="flow-row"><div class="fstep"><div class="fs-n">01</div><div class="fs-t">공고</div><div class="fs-d">필요한 물품과 조건을 공개적으로 알립니다. 부품, 연료, 급식 재료, 공사까지 대상은 다양합니다.</div></div><div class="fstep"><div class="fs-n">02</div><div class="fs-t">응찰</div><div class="fs-d">팔고 싶은 업체가 가격을 써서 참여합니다. 참여한 업체 수가 곧 경쟁의 크기입니다.</div></div><div class="fstep"><div class="fs-n">03</div><div class="fs-t">개찰</div><div class="fs-d">정해진 날에 제출된 가격을 열어 확인합니다.</div></div><div class="fstep"><div class="fs-n">04</div><div class="fs-t">낙찰</div><div class="fs-d">조건에 맞는 업체를 선정해 계약합니다. 여기까지 오면 정상입니다.</div></div><div class="fstep fail"><div class="fs-n">04'</div><div class="fs-t">유찰</div><div class="fs-d">계약이 성립하지 않은 상태입니다. 공고를 처음부터 다시 내야 합니다.</div></div></div><div class="flow-note">유찰이 나면 <b>공고 게시부터 개찰까지 전 과정을 반복</b>합니다. 물건값이 오르는 것이 아니라 시간이 사라지고, 그 끝에는 부대의 물자 수령 지연이 있습니다.<br>이 분석의 핵심 발견은 <b>유찰의 대부분이 2단계에서 아무도 오지 않아 발생한다</b>는 것입니다. 경쟁이 약했던 것이 아니라, 팔겠다는 업체가 없었습니다.</div></div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="ledger"><div><div class="lg-k">전체 유찰률</div><div class="lg-v">{D['유찰'].mean()*100:.1f}<span style="font-size:1rem">%</span></div><div class="lg-n">공고 4건 중 약 1건이 계약에 이르지 못함</div></div><div><div class="lg-k">유찰 중 무응찰</div><div class="lg-v sig">92.7<span style="font-size:1rem">%</span></div><div class="lg-n">유찰 건의 대부분은 응찰 업체가 0곳</div></div><div><div class="lg-k">공급 두께–유찰 상관</div><div class="lg-v">−0.729</div><div class="lg-n">응찰 업체가 많은 품목일수록 유찰이 적음<br>(−1에 가까울수록 강한 반비례)</div></div><div><div class="lg-k">6년간 추세</div><div class="lg-v">없음</div><div class="lg-n">개선도 악화도 없는 만성적 구조<br>(연 +0.01%p, 통계적 의미 없음)</div></div></div>""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["공급취약도", "공고 사전진단", "재공고 경보", "품목 상세"])

# ── 1 ─────────────────────────────────────────────────────────
with t1:
    sec("01", "무엇을 사느냐가 유찰을 결정한다",
        "품목별로 유찰률을 세어 봤습니다. 같은 군이 발주하는데도 품목에 따라 결과가 크게 갈립니다.")

    g = (D.dropna(subset=["품목대분류"]).groupby("품목대분류")
         .agg(건수=("유찰", "size"), 유찰률=("유찰", "mean"), 중앙응찰=("응찰수", "median"))
         .reset_index())
    g = g[g["건수"] >= 25].sort_values("유찰률")

    howto("이 그래프 읽는 법",
          "막대가 길수록 그 품목의 유찰이 잦다는 뜻입니다. "
          "<span style='color:#B4232A;font-weight:600'>붉은 막대</span>는 유찰률 30% 이상, "
          "<span style='color:#3E5C76;font-weight:600'>푸른 막대</span>는 15% 미만입니다. "
          "막대에 마우스를 올리면 공고 건수와 평소 응찰 업체 수가 함께 표시됩니다.")

    fig = go.Figure(go.Bar(
        x=g["유찰률"], y=g["품목대분류"], orientation="h",
        marker=dict(color=[SEAL if v >= .30 else (SLATE if v >= .15 else STEEL)
                           for v in g["유찰률"]]),
        text=[f"{v*100:.1f}%" for v in g["유찰률"]], textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=11),
        customdata=np.stack([g["건수"], g["중앙응찰"]], axis=-1),
        hovertemplate="<b>%{y}</b><br>유찰률 %{x:.1%}<br>공고 %{customdata[0]}건"
                      "<br>평소 응찰 %{customdata[1]:.0f}곳<extra></extra>"))
    fig.update_layout(template=PLOT, height=max(400, 27 * len(g)),
                      xaxis=dict(tickformat=".0%", range=[0, g["유찰률"].max() * 1.18],
                                 title="유찰률"),
                      yaxis=dict(title=""), showlegend=False, bargap=.42)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="note">위쪽에 몰린 품목은 차량·기동장비, 항공·함정, 화기·탄약처럼 '
                '<b>군에서만 쓰는 특수품</b>입니다. 민간에서 사지 않으니 만드는 업체도 적습니다.<br>'
                '아래쪽은 시설공사·급식처럼 <b>민간 시장과 공급자를 공유하는 품목</b>입니다. '
                '건설사도 식자재 업체도 많으니 부를 곳이 많습니다.</div>', unsafe_allow_html=True)

    sec("02", "왜 그런가 — 공급 두께의 문제",
        "'공급 두께'란 그 품목을 팔 수 있는 업체가 시장에 얼마나 있는지를 뜻합니다. "
        "직접 셀 수는 없지만, 평소 그 품목 공고에 몇 곳이 응찰하는지로 가늠할 수 있습니다.")

    howto("이 그래프 읽는 법",
          "가로축은 그 품목 공고에 평소 응찰하는 업체 수, 세로축은 유찰률입니다. "
          "점의 크기는 공고 건수입니다. <span style='color:#16202C;font-weight:600'>왼쪽 아래로 갈수록 위험</span>합니다 "
          "— 부를 업체가 적고 실제로 유찰도 잦다는 뜻입니다. "
          "업체 수 차이가 워낙 커서 가로축은 로그 눈금을 썼습니다(1 → 10 → 100이 같은 간격).")

    g2 = g.copy(); g2["표시"] = g2["중앙응찰"].clip(lower=.5)
    lab = (g2.nlargest(4, "유찰률")["품목대분류"].tolist()
           + g2.nsmallest(3, "유찰률")["품목대분류"].tolist())
    g2["라벨"] = g2["품목대분류"].where(g2["품목대분류"].isin(lab), "")
    f2 = px.scatter(g2, x="표시", y="유찰률", size="건수", text="라벨", log_x=True,
                    hover_name="품목대분류", size_max=44,
                    color="유찰률", color_continuous_scale=[[0, STEEL], [.5, SLATE], [1, SEAL]],
                    labels={"표시": "평소 응찰 업체 수 (로그 눈금)", "유찰률": "유찰률"})
    f2.update_traces(textposition="top center", textfont=dict(size=10.5),
                     marker=dict(line=dict(width=1.2, color=PAPER)))
    f2.update_layout(template=PLOT, height=430, coloraxis_showscale=False,
                     yaxis=dict(tickformat=".0%"))
    st.plotly_chart(f2, use_container_width=True)

    st.markdown('<div class="note"><b>연료·유류</b>는 평소 응찰이 0곳에 가깝고 유찰률이 65%입니다. '
                '반면 <b>실험·측정기기</b>는 평소 200곳 넘게 응찰하고 유찰률은 13%입니다.<br>'
                '이 관계를 하나의 숫자로 나타낸 것이 <b>상관계수 −0.729</b>입니다. '
                '0이면 아무 관계 없음, −1이면 완벽한 반비례를 뜻하므로 −0.729는 상당히 강한 반비례입니다.'
                '</div>', unsafe_allow_html=True)

    with st.expander("품목별 수치를 표로 보기"):
        st.dataframe(g.sort_values("유찰률", ascending=False)
                     .rename(columns={"중앙응찰": "평소 응찰 업체 수", "건수": "공고 건수"})
                     .style.format({"유찰률": "{:.1%}", "평소 응찰 업체 수": "{:.0f}"}),
                     use_container_width=True, height=420, hide_index=True)

# ── 2 ─────────────────────────────────────────────────────────
with t2:
    sec("03", "공고를 내기 전에 진단합니다",
        "발주 조건을 입력하면 응찰 업체가 없을 위험을 세 등급으로 알려드립니다.")

    st.markdown(f"""    <div class="grades"><div class="gr"><div class="gr-n hi">고위험</div><div class="gr-d">이 등급을 받은 과거 공고 중<br>실제로 응찰이 없었던 비율</div><div class="gr-v" style="color:{SEAL}">78.0%</div></div><div class="gr"><div class="gr-n">주의</div><div class="gr-d">이 등급을 받은 과거 공고 중<br>실제로 응찰이 없었던 비율</div><div class="gr-v">47.5%</div></div><div class="gr"><div class="gr-n">양호</div><div class="gr-d">이 등급을 받은 과거 공고 중<br>실제로 응찰이 없었던 비율</div><div class="gr-v">15.9%</div></div></div>""", unsafe_allow_html=True)

    howto("이 진단의 구조",
          "① 조건을 넣으면 <span style='color:#16202C;font-weight:600'>예측 모델</span>(2020~2023년 학습)이 "
          "위험 점수를 계산하고, 점수 구간에 따라 등급이 정해집니다. "
          "② 등급 옆의 %는 예측이 아니라 <span style='color:#16202C;font-weight:600'>검증 실적</span>입니다 — "
          "2025년 공고 중 같은 등급을 받았던 건들이 실제로 어떻게 됐는지를 보여줍니다. "
          "③ 그 아래 '진단 근거'는 선택한 기관·품목의 <span style='color:#16202C;font-weight:600'>과거 6개년 실적</span>으로, "
          "모델이 가장 크게 참조하는 값입니다. 선택을 바꾸면 점수와 근거가 함께 움직입니다.")

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        ORG_ETC = "(목록에 없는 기관 · 신규 발주)"
        org = st.selectbox("수요기관", [ORG_ETC] + sorted(L["org_map"].keys()),
                           index=1 + sorted(L["org_map"].keys()).index("육군군수사령부")
                                 if "육군군수사령부" in L["org_map"] else 0,
                           help="2020~2025년에 실제 발주 이력이 있는 기관 목록입니다. "
                                "목록에 없는 부대는 맨 위 항목을 선택하면 품목 기준으로 진단합니다.")
        item = st.selectbox("품목 대분류", sorted(L["item_map"].keys()),
                            help="정부 표준 품명분류 기준입니다.")
        biz = st.selectbox("업무구분", L["cats"]["업무구분"],
                           help="물품 구매인지, 용역인지, 공사인지 구분합니다.")
        method = st.selectbox("계약방법", L["cats"]["계약방법"],
                              help="일반경쟁은 누구나, 제한경쟁은 자격을 갖춘 업체만 참여할 수 있습니다.")
    with c2:
        mfr = st.radio("제조물품제한", ["N", "Y"], horizontal=True,
                       help="직접 제조하는 업체만 입찰하도록 한정하는 조건입니다. 유통·중개 업체가 "
                            "배제되어 부를 수 있는 업체가 줄어듭니다. 분석 결과 비교 가능한 21개 품목 "
                            "중 19개에서 유찰률이 평균 24.3%p 높았습니다.")
        ind = st.radio("업종제한", ["N", "Y"], horizontal=True,
                       help="특정 면허·업종을 가진 업체로 참여를 제한합니다.")
        urgent = st.radio("긴급공고", ["N", "Y"], horizontal=True,
                          help="통상보다 짧은 기간으로 급히 내는 공고입니다.")
        rn = st.checkbox("재공고 건", help="이전에 한 번 유찰되어 다시 올리는 공고입니다.")
        st.markdown('<div class="note"><b>공고기간은 왜 없나요?</b><br>'
                    '유찰된 공고와 성사된 공고의 평균 공고기간이 8.1일로 같았습니다. '
                    '기간을 늘려도 유찰이 줄지 않는다는 뜻이라, 근거 없는 조작 기능은 넣지 않았습니다.'
                    '</div>', unsafe_allow_html=True)

    if st.button("진단하기", use_container_width=True):
        p, ir, orr = predict(None if org == ORG_ETC else org, item, biz, method, mfr, urgent, ind, rn)
        lv = "고위험" if p >= HI else ("주의" if p >= MID else "양호")
        hi = "hi" if lv == "고위험" else ""
        score = round(p * 100)
        acts = {
            "고위험": "사전 시장조사로 공급 가능 업체 확인 · 수요통합 검토(소량으로 나눠 발주하지 않기) · "
                   "사업 일정에 여유 확보 · 수의계약 전환 절차 미리 준비",
            "주의": "제조물품제한이 꼭 필요한지 재검토 · 같은 품목의 과거 응찰 이력 확인",
            "양호": "통상 절차대로 진행하셔도 됩니다."}
        st.markdown(f"""<div class="verdict {hi}"><div class="v-grade {hi}">{lv}</div><div class="score-line"><span class="score-v">{score}</span><span class="score-c">/ 100점 · 예측 모델의 무응찰 위험 점수</span></div><div class="meter-wrap"><div class="meter"><div class="meter-pin" style="left:calc({max(2, min(98, score))}% - 1.5px)"></div></div><div class="meter-lab"><span>0 양호</span><span class="l30">30 주의</span><span class="l50">50 고위험</span><span class="l100">100</span></div></div><div class="v-fact" style="margin-top:.7rem">검증 실적 — 같은 등급을 받은 과거 공고 가운데 <b>{STAT[lv]}%</b>가 실제로 응찰 업체가 한 곳도 없었습니다.</div><div class="v-act"><b>권고 조치</b>{acts[lv]}</div></div>""", unsafe_allow_html=True)

        org_v = f"{orr['rate']*100:.1f}%" if orr["n"] else "실적 없음"
        org_n = f"공고 {orr['n']:,}건 기준" if orr["n"] else "품목 기준으로 진단함"
        both = D[(D["수요기관"] == org) & (D["품목대분류"] == item)] if org != ORG_ETC else D.iloc[0:0]
        both_v = f"{both['무응찰'].mean()*100:.1f}%" if len(both) >= 3 else "—"
        both_n = f"공고 {len(both):,}건 기준" if len(both) >= 3 else "사례 3건 미만"
        st.markdown(f"""<div class="basis"><div class="bi"><div class="bi-k">이 품목의 과거 무응찰률</div><div class="bi-v">{ir['rate']*100:.1f}%</div><div class="bi-n">공고 {ir['n']:,}건 기준</div></div><div class="bi"><div class="bi-k">이 기관의 과거 무응찰률</div><div class="bi-v">{org_v}</div><div class="bi-n">{org_n}</div></div><div class="bi"><div class="bi-k">이 기관 × 이 품목</div><div class="bi-v">{both_v}</div><div class="bi-n">{both_n}</div></div></div>""", unsafe_allow_html=True)
        st.markdown('<div class="note">위 세 값은 예측이 아니라 2020~2025년 <b>과거 실적</b>이며, 모델이 가장 크게 참조하는 입력입니다. 기관·품목을 바꾸면 점수와 함께 달라집니다.</div>', unsafe_allow_html=True)

        if mfr == "Y":
            st.markdown('<div class="note">제조물품제한을 해제하면 위험도가 낮아질 수 있습니다. '
                        '다만 이는 상관관계이지 인과관계로 확인된 것은 아니며, '
                        '제한의 필요성은 건별로 판단하셔야 합니다.</div>', unsafe_allow_html=True)

        s = both
        if len(s):
            st.markdown(f'<div class="sec" style="margin-top:1.6rem"><span class="sec-n">최근 기록</span><span class="sec-t">{org} · {item}</span><div class="sec-d">이 조합의 최근 공고와 결과입니다. 아래 표식은 평소 응찰 규모입니다.</div></div>', unsafe_allow_html=True)
            st.markdown(tally(s["응찰수"].median()), unsafe_allow_html=True)
            st.dataframe(s[["공고일자", "공고명", "응찰수", "입찰진행상태값"]].tail(8)
                         .rename(columns={"입찰진행상태값": "결과", "응찰수": "응찰 업체 수"}),
                         use_container_width=True, hide_index=True)
        elif org != ORG_ETC:
            st.markdown('<div class="note">이 기관과 품목 조합의 과거 기록이 없습니다. 진단은 품목 전체 실적과 기관 전체 실적을 기준으로 산출했습니다.</div>', unsafe_allow_html=True)

# ── 3 ─────────────────────────────────────────────────────────
with t3:
    sec("04", "재공고는 회복 수단이 아니다",
        "유찰이 나면 보통 같은 내용으로 공고를 다시 올립니다. 그 결과가 어땠는지 확인했습니다.")

    howto("이 그래프 읽는 법",
          "'등록공고'는 처음 올린 공고, '재공고'는 유찰된 뒤 다시 올린 공고입니다. "
          "재공고의 유찰률이 처음 공고보다 "
          "<span style='color:#B4232A;font-weight:600'>약 2.8배 높습니다</span>. "
          "다시 올려도 절반 이상은 또 아무도 오지 않았다는 뜻입니다.")

    r = D.groupby("공고상태값").agg(건수=("유찰", "size"), 유찰률=("유찰", "mean")).reset_index()
    r = r[r["건수"] >= 50].sort_values("유찰률")
    f3 = go.Figure(go.Bar(x=r["공고상태값"], y=r["유찰률"],
                          marker_color=[SEAL if v > .5 else SLATE for v in r["유찰률"]],
                          text=[f"{v*100:.1f}%" for v in r["유찰률"]], textposition="outside",
                          textfont=dict(family="IBM Plex Mono", size=13),
                          hovertemplate="<b>%{x}</b><br>유찰률 %{y:.1%}<extra></extra>"))
    f3.update_layout(template=PLOT, height=330,
                     yaxis=dict(tickformat=".0%", range=[0, .72], title=""),
                     xaxis=dict(title=""), bargap=.55,
                     margin=dict(t=20, b=44, l=64, r=20))
    st.plotly_chart(f3, use_container_width=True)

    st.markdown('<div class="note"><b>왜 이런 일이 생기나요?</b><br>'
                '유찰의 원인이 공고 내용이 아니라 <b>그 품목을 만들 업체가 없다는 데</b> 있기 때문입니다. '
                '같은 조건으로 다시 물어봐도 대답할 곳이 없는 것입니다.<br>'
                '재공고에 앞서 <b>수요통합</b>(여러 부대 물량을 묶어 규모를 키움), '
                '<b>규격 재검토</b>, <b>수의계약 전환</b>을 먼저 고려하는 편이 낫습니다. '
                '분석 대상 중에는 6차까지 반복된 사례도 있었습니다.</div>', unsafe_allow_html=True)

    rep = D[D["공고상태값"] == "재공고"].dropna(subset=["품목대분류"])
    t = rep.groupby("품목대분류").agg(재공고건수=("유찰", "size"), 재유찰률=("유찰", "mean"))
    st.markdown('<div class="sec" style="margin-top:2rem"><span class="sec-n">품목별</span>'
                '<span class="sec-t">다시 올려도 또 유찰되는 비율</span></div>',
                unsafe_allow_html=True)
    st.dataframe(t[t["재공고건수"] >= 10].sort_values("재유찰률", ascending=False)
                 .rename(columns={"재공고건수": "재공고 건수", "재유찰률": "다시 유찰된 비율"})
                 .style.format({"다시 유찰된 비율": "{:.1%}"}), use_container_width=True)

# ── 4 ─────────────────────────────────────────────────────────
with t4:
    sec("05", "품목별 상세", "궁금한 품목을 골라 연도별 추이와 기관별 현황을 확인하실 수 있습니다.")
    p4 = st.selectbox("품목 선택", sorted(D["품목대분류"].dropna().unique()),
                      label_visibility="collapsed")
    s = D[D["품목대분류"] == p4]

    st.markdown(f"""    <div class="ledger"><div><div class="lg-k">공고 건수</div><div class="lg-v">{len(s):,}</div><div class="lg-n">2020–2025 누적</div></div><div><div class="lg-k">유찰률</div><div class="lg-v {'sig' if s['유찰'].mean() >= .3 else ''}">{s['유찰'].mean()*100:.1f}<span style="font-size:1rem">%</span></div><div class="lg-n">계약에 이르지 못한 비율</div></div><div><div class="lg-k">무응찰률</div><div class="lg-v">{s['무응찰'].mean()*100:.1f}<span style="font-size:1rem">%</span></div><div class="lg-n">응찰 업체가 0곳이었던 비율</div></div><div><div class="lg-k">평소 응찰 업체</div><div class="lg-v">{s['응찰수'].median():.0f}<span style="font-size:1rem">곳</span></div><div class="lg-n">중앙값 기준</div></div></div>""", unsafe_allow_html=True)
    st.markdown(tally(s["응찰수"].median()), unsafe_allow_html=True)

    yr = s.groupby("연도").agg(유찰률=("유찰", "mean")).reset_index()
    f4 = go.Figure(go.Scatter(x=yr["연도"], y=yr["유찰률"], mode="lines+markers",
                              line=dict(color=INK, width=2),
                              marker=dict(size=8, color=SEAL, line=dict(width=2, color=PAPER)),
                              hovertemplate="%{x}년 · 유찰률 %{y:.1%}<extra></extra>"))
    f4.update_layout(template=PLOT, height=300,
                     yaxis=dict(tickformat=".0%", rangemode="tozero", title=""),
                     xaxis=dict(title=""), margin=dict(t=20, b=44, l=64, r=20))
    st.plotly_chart(f4, use_container_width=True)

    o = s.groupby("수요기관").agg(건수=("유찰", "size"), 유찰률=("유찰", "mean"))
    if len(o[o["건수"] >= 10]):
        st.markdown('<div class="note">같은 품목이라도 기관에 따라 유찰률이 다릅니다. '
                    '공고 10건 이상인 기관만 표시했습니다.</div>', unsafe_allow_html=True)
        st.dataframe(o[o["건수"] >= 10].sort_values("유찰률", ascending=False)
                     .rename(columns={"건수": "공고 건수"})
                     .style.format({"유찰률": "{:.1%}"}), use_container_width=True)

# ── 용어 설명 ─────────────────────────────────────────────────
with st.expander("용어 설명 — 처음 보시는 분을 위해"):
    st.markdown("""    <div class="gloss"><div class="gi"><div class="gi-t">유찰</div><div class="gi-d">입찰이 성립하지 않아 낙찰자를 정하지 못한 상태. 공고를 다시 내야 합니다.</div></div><div class="gi"><div class="gi-t">무응찰</div><div class="gi-d">공고를 냈는데 참여한 업체가 한 곳도 없는 경우. 유찰의 92.7%가 여기 해당합니다.</div></div><div class="gi"><div class="gi-t">단독응찰</div><div class="gi-d">한 곳만 참여한 경우. 경쟁이 성립하지 않아 재공고 대상이 될 수 있습니다.</div></div><div class="gi"><div class="gi-t">개찰</div><div class="gi-d">정해진 날에 제출된 입찰 가격을 열어 확인하는 절차입니다.</div></div><div class="gi"><div class="gi-t">재공고</div><div class="gi-d">유찰된 건을 다시 공고하는 것. 법에 정해진 정규 절차입니다.</div></div><div class="gi"><div class="gi-t">수의계약</div><div class="gi-d">경쟁 없이 특정 업체와 직접 맺는 계약. 재공고 후에도 참여자가 없으면 전환할 수 있습니다.</div></div><div class="gi"><div class="gi-t">수요기관</div><div class="gi-d">그 물품을 실제로 사용할 부대·기관입니다. 공고를 대행하는 기관과 다를 수 있습니다.</div></div><div class="gi"><div class="gi-t">제조물품제한</div><div class="gi-d">직접 제조하는 업체만 입찰하도록 한정하는 조건. 유통업체가 배제되어 참여 가능 업체가 줄어듭니다.</div></div><div class="gi"><div class="gi-t">공급 두께</div><div class="gi-d">그 품목을 팔 수 있는 업체가 시장에 얼마나 있는지. 이 분석에서는 평소 응찰 업체 수로 가늠했습니다.</div></div><div class="gi"><div class="gi-t">수요통합</div><div class="gi-d">여러 부대의 물량을 묶어 한 번에 발주하는 것. 규모가 커지면 업체가 참여할 이유가 생깁니다.</div></div><div class="gi"><div class="gi-t">상관계수</div><div class="gi-d">두 값이 함께 움직이는 정도. 0이면 무관, −1이면 완벽한 반비례입니다.</div></div><div class="gi"><div class="gi-t">ROC-AUC</div><div class="gi-d">예측 모델의 판별력. 0.5는 찍는 수준, 1.0은 완벽. 0.806은 10번 중 약 8번 올바르게 구별한다는 뜻입니다.</div></div></div>""", unsafe_allow_html=True)

st.markdown("""<div class="foot">자료 · 조달정보개방포털 입찰공고 내역 (2020–2025, 국방부 하위기관 포함) · 방위사업청 공개데이터<br>모델 · LightGBM · 학습 2020–23 / 검증 2024 / 시험 2025 시간분할 · ROC-AUC 0.806 (단순규칙 0.664)<br>2026년 육군 빅데이터 분석 경연대회 출품작</div>""", unsafe_allow_html=True)
