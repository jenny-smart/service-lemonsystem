# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(
    page_title="檸檬服務系統",
    page_icon="🍋",
    layout="wide",
    initial_sidebar_state="expanded",
)

LEMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Space+Grotesk:wght@500;700&display=swap');

:root {
    --lemon: #F5C518;
    --lemon-dark: #D4A017;
    --lemon-soft: #FFFDF3;
    --lemon-mid: #FFF3C4;
    --charcoal: #1C1C1E;
    --ink: #3A3A3C;
    --muted: #8E8E93;
    --border: #E8E8EC;
    --surface: #FFFFFF;
    --success: #34C759;
    --danger: #FF3B30;
    --radius: 18px;
    --shadow: 0 8px 28px rgba(0,0,0,0.06);
}

html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
    color: var(--charcoal);
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stAppViewContainer"] { background: #FAFAFA; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1180px !important;
}

.hero {
    background: linear-gradient(135deg, #FFFDF5 0%, #FFF7D1 100%);
    border: 1.5px solid var(--lemon-mid);
    border-radius: var(--radius);
    padding: 2.2rem 2.6rem;
    margin-bottom: 1.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 8px 28px rgba(245,197,24,0.12);
}
.hero-title {
    font-family: 'Space Grotesk', 'Noto Sans TC', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.6px;
}
.hero-sub {
    color: var(--ink);
    font-size: 0.98rem;
    margin-top: 0.45rem;
    line-height: 1.7;
    opacity: 0.78;
}
.hero-emoji { font-size: 3.2rem; }

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.3rem 1.4rem;
    box-shadow: var(--shadow);
    min-height: 168px;
}
.card-title {
    font-size: 1.08rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
}
.card-desc {
    color: var(--ink);
    font-size: 0.92rem;
    line-height: 1.7;
    opacity: 0.82;
}
.badge {
    display: inline-block;
    background: var(--lemon-mid);
    border-radius: 999px;
    padding: 0.22rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 800;
    margin-bottom: 0.75rem;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 900;
    margin: 1.4rem 0 0.8rem;
}
.info-strip {
    background: var(--lemon-soft);
    border-left: 5px solid var(--lemon);
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.15rem;
    color: var(--ink);
    line-height: 1.7;
    margin-bottom: 1.1rem;
}
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--border);
}
.stButton > button {
    background: var(--lemon) !important;
    color: var(--charcoal) !important;
    border: none !important;
    border-radius: 13px !important;
    font-weight: 800 !important;
    padding: 0.65rem 1rem !important;
    box-shadow: 0 4px 14px rgba(245,197,24,0.28) !important;
}
.stButton > button:hover {
    background: var(--lemon-dark) !important;
    transform: translateY(-1px);
}
</style>
"""

st.markdown(LEMON_CSS, unsafe_allow_html=True)

PAGES = {
    "首頁總覽": "home",
    "服務訂單系統": "orders",
    "客服備註 / 營運工具": "memo",
    "排班工具": "shift",
    "ATM 對帳": "atm",
    "服務異動": "change_order",
}

with st.sidebar:
    st.markdown("### 🍋 檸檬服務系統")
    st.caption("Service Lemon System")
    selected_label = st.radio("功能選單", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.caption("先完成統一入口與版型，再逐步掛入 orders-system / memo-system 功能。")

page = PAGES[selected_label]

st.markdown(
    """
    <div class="hero">
      <div>
        <div class="hero-title">檸檬服務系統</div>
        <div class="hero-sub">整合服務訂單、客服備註、排班、ATM 對帳與服務異動的營運入口。</div>
      </div>
      <div class="hero-emoji">🍋</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def card(title: str, badge: str, desc: str):
    st.markdown(
        f"""
        <div class="card">
          <div class="badge">{badge}</div>
          <div class="card-title">{title}</div>
          <div class="card-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if page == "home":
    st.markdown('<div class="info-strip">目前先套用新版入口版型。下一步會把 orders-system 與 memo-system 的實際功能模組接進各分頁。</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        card("服務訂單系統", "orders-system", "批次建單、單筆快速建單、查詢會員、查班表、LINE 通知與確認信。")
    with c2:
        card("客服備註 / 營運工具", "memo-system", "查詢歷史訂單、回填客服備註、處理新成單提醒與營運資料。")
    with c3:
        card("財務與異動", "operations", "ATM 對帳、付款更新、退款處理、服務異動費試算與後台同步。")

elif page == "orders":
    st.markdown('<div class="section-title">服務訂單系統</div>', unsafe_allow_html=True)
    st.info("這裡將掛入 orders-system 的 ordersapp.py / orders.py / quick_order.py。")
    st.button("進入建單流程", use_container_width=True)

elif page == "memo":
    st.markdown('<div class="section-title">客服備註 / 營運工具</div>', unsafe_allow_html=True)
    st.info("這裡將掛入 memo-system 的 memoapp.py / memo.py 功能。")
    st.button("進入備註回填", use_container_width=True)

elif page == "shift":
    st.markdown('<div class="section-title">排班工具</div>', unsafe_allow_html=True)
    st.info("這裡將掛入 memo-system 的 shift.py 排班匯入、空檔查詢與清空排班。")

elif page == "atm":
    st.markdown('<div class="section-title">ATM 對帳</div>', unsafe_allow_html=True)
    st.info("這裡將掛入 memo-system 的 atm.py 對帳流程。")

elif page == "change_order":
    st.markdown('<div class="section-title">服務異動</div>', unsafe_allow_html=True)
    st.info("這裡將掛入 memo-system 的 change_order.py 異動試算與後台同步。")
