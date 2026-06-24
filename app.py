# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(
    page_title="檸檬營運自動化工具",
    page_icon="🍋",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&display=swap');
:root {
    --lemon:#F5C518; --lemon-dark:#D4A017; --lemon-soft:#FFFCF2;
    --lemon-mid:#FFF3C4; --charcoal:#1C1C1E; --ink:#3A3A3C;
    --muted:#8E8E93; --border:#E8E8EC; --surface:#FFFFFF;
    --radius:16px; --shadow:0 2px 14px rgba(0,0,0,0.05);
}
html, body, [class*="css"] { font-family:'Noto Sans TC', sans-serif; color:var(--charcoal); }
#MainMenu, footer, header { visibility:hidden; }
[data-testid="stAppViewContainer"] { background:#FAFAFA; }
.block-container { padding-top:2.2rem !important; padding-bottom:2.5rem !important; max-width:1180px !important; }
.hero {
    background:linear-gradient(135deg,#FFFDF5 0%,#FFFBEA 100%);
    border:1.5px solid var(--lemon-mid); border-radius:var(--radius);
    padding:2.1rem 2.6rem; margin-bottom:2.2rem; display:flex;
    align-items:center; gap:1.3rem; box-shadow:0 2px 14px rgba(245,197,24,0.08);
}
.hero-emoji { font-size:3.1rem; line-height:1; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; margin:0; letter-spacing:-0.5px; }
.hero-sub { color:var(--ink); font-size:0.94rem; margin-top:0.35rem; opacity:0.75; line-height:1.6; }
.step-pill { display:inline-flex; align-items:center; gap:0.6rem; background:var(--surface); border:1.5px solid var(--lemon-mid); border-radius:30px; padding:0.4rem 1.1rem 0.4rem 0.5rem; font-size:0.98rem; font-weight:900; margin-bottom:1.1rem; box-shadow:0 2px 8px rgba(245,197,24,0.10); }
.step-num { background:var(--lemon); border-radius:50%; width:26px; height:26px; display:inline-flex; align-items:center; justify-content:center; font-size:0.85rem; font-weight:900; box-shadow:0 1px 4px rgba(212,160,23,0.4); }
.info-strip { background:var(--lemon-soft); border-left:4px solid var(--lemon); border-radius:0 10px 10px 0; padding:0.75rem 1.1rem; font-size:0.9rem; color:var(--ink); margin-bottom:1rem; }
.preview-card { border:1px solid var(--border); border-radius:var(--radius); padding:20px 22px; margin-bottom:16px; background:white; box-shadow:var(--shadow); }
.preview-title { font-size:18px; font-weight:900; margin-bottom:8px; }
.preview-sub { color:#444; font-size:14px; line-height:1.8; }
.stButton > button { background:var(--lemon) !important; color:var(--charcoal) !important; border:none !important; border-radius:12px !important; font-weight:700 !important; font-family:'Noto Sans TC',sans-serif !important; font-size:15px !important; padding:0.6rem 1.2rem !important; box-shadow:0 3px 12px rgba(245,197,24,0.30) !important; }
.stButton > button:hover { background:var(--lemon-dark) !important; transform:translateY(-1px) !important; box-shadow:0 4px 16px rgba(245,197,24,0.40) !important; }
a { color:var(--charcoal); font-weight:900; text-decoration:none; }
hr { border-color:#ececec !important; margin:1.6rem 0 !important; }
</style>
""", unsafe_allow_html=True)

MEMO_APP_URL = "https://memo-lemon-system.streamlit.app/"
ORDERS_APP_URL = "https://orders-lemon-system.streamlit.app/"


def step(num, title):
    st.markdown(f'<div class="step-pill"><span class="step-num">{num}</span>{title}</div>', unsafe_allow_html=True)


def card(title, body, url):
    st.markdown(f"""
    <div class="preview-card">
        <div class="preview-title">{title}</div>
        <div class="preview-sub">{body}</div>
        <div style="margin-top:12px;"><a href="{url}" target="_blank">開啟功能 ↗</a></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-emoji">🍋</div>
  <div>
    <div class="hero-title">檸檬營運自動化工具</div>
    <div class="hero-sub">客服・排班・財務・服務異動・快速訂單整合入口</div>
  </div>
</div>
""", unsafe_allow_html=True)

step("1", "選擇功能")
section = st.selectbox(
    "功能",
    ["📋 客服 / Memo 系統", "🧾 快速訂單系統"],
    label_visibility="collapsed",
)

st.markdown("""
<div class="info-strip"><b>整合說明</b><ul>
<li>本頁沿用 memo-system 的檸檬黃網頁模板。</li>
<li>目前先做為新系統入口，避免重新設計新模板。</li>
<li>確認入口與部署正常後，再把 memo / orders 功能模組逐步搬入本 repo。</li>
</ul></div>
""", unsafe_allow_html=True)

if section == "📋 客服 / Memo 系統":
    card(
        "📋 客服 / Memo 系統",
        "客服作業、排班管理、財務對帳、服務異動、評估文字工具。",
        MEMO_APP_URL,
    )
else:
    card(
        "🧾 快速訂單系統",
        "訂單建立、會員查詢、時段確認、一般 / VIP 客戶下單流程。",
        ORDERS_APP_URL,
    )

st.markdown("---")
st.caption("service-lemonsystem · memo template · combined entry")
