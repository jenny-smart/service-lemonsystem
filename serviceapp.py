# -*- coding: utf-8 -*-
import streamlit as st

from orders import (
    old_customer_quick_order,
    new_customer_parser,
    line_notice_generator,
    order_converter,
    stored_value_makeup,
)

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
    border:1.5px solid var(--lemon-mid);
    border-radius:var(--radius);
    padding:2.1rem 2.6rem;
    margin-bottom:2.2rem;
    display:flex;
    align-items:center;
    gap:1.3rem;
    box-shadow:0 2px 14px rgba(245,197,24,0.08);
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
hr { border-color:#ececec !important; margin:1.6rem 0 !important; }
</style>
""", unsafe_allow_html=True)

MEMO_APP_URL = "https://memo-lemon-system.streamlit.app/"


def step(num, title):
    st.markdown(f'<div class="step-pill"><span class="step-num">{num}</span>{title}</div>', unsafe_allow_html=True)


def render_memo_placeholder(title, description):
    step("2", title)
    st.markdown(
        f"""
        <div class="info-strip"><b>{title}</b><ul>
        <li>{description}</li>
        <li>此功能會沿用 memo-system 版型，後續逐步搬入 service-lemonsystem。</li>
        <li>目前先保留入口，不修改 memo-system 原 repo。</li>
        </ul></div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("開啟目前 Memo 系統", MEMO_APP_URL, use_container_width=True)


st.markdown("""
<div class="hero">
  <div class="hero-emoji">🍋</div>
  <div>
    <div class="hero-title">檸檬營運自動化工具</div>
    <div class="hero-sub">客服・排班・財務・服務異動・評估・快速訂單</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-strip"><b>目前階段</b><ul>
<li>所有功能放在同一層選單。</li>
<li>只修改 service-lemonsystem。</li>
<li>memo-system 與 orders-system 保持不動。</li>
</ul></div>
""", unsafe_allow_html=True)

step("1", "選擇功能")
feature = st.selectbox(
    "功能",
    [
        "📋 客服作業",
        "📅 排班管理",
        "💰 財務對帳",
        "🔄 服務異動",
        "📐 評估文字工具",
        "新客資料拆解",
        "舊客快速建單",
        "LINE 通知產生器",
        "訂單轉換",
        "儲值金補價差",
    ],
    label_visibility="collapsed",
)

st.markdown("---")

if feature == "📋 客服作業":
    render_memo_placeholder("📋 客服作業", "舊客回購備註回填、新成單提醒建立、客服備忘錄整理。")

elif feature == "📅 排班管理":
    render_memo_placeholder("📅 排班管理", "排班匯入、檸檬人空檔查詢、清空排班。")

elif feature == "💰 財務對帳":
    render_memo_placeholder("💰 財務對帳", "待付款清單查詢、ATM 配對、系統對帳更新。")

elif feature == "🔄 服務異動":
    render_memo_placeholder("🔄 服務異動", "車馬費、異動費、加減時、退款與後台同步。")

elif feature == "📐 評估文字工具":
    render_memo_placeholder("📐 評估文字工具", "貼入評估內容，自動產生兩版客服文字與金額計算。")

elif feature == "舊客快速建單":
    step("2", "舊客快速建單")
    name = st.text_input("客戶姓名", placeholder="例如：王小明")
    phone = st.text_input("電話", placeholder="例如：0912345678")
    address = st.text_input("地址", placeholder="請輸入服務地址")
    if st.button("建立舊客快速建單資料", use_container_width=True):
        st.success(old_customer_quick_order.run(name or phone or address or "未輸入"))

elif feature == "新客資料拆解":
    step("2", "新客資料拆解")
    raw_text = st.text_area("貼上新客資料", height=220, placeholder="貼上 LINE / 表單 / 訂單文字")
    if st.button("拆解資料", use_container_width=True):
        st.json(new_customer_parser.parse(raw_text))

elif feature == "LINE 通知產生器":
    step("2", "LINE 通知產生器")
    order_no = st.text_input("訂單編號", placeholder="例如：LC002115751")
    customer = st.text_input("客戶名稱")
    if st.button("產生 LINE 通知", use_container_width=True):
        msg = line_notice_generator.generate({"order_no": order_no, "customer": customer})
        st.text_area("LINE 通知內容", value=msg, height=220)

elif feature == "訂單轉換":
    step("2", "訂單轉換")
    source_order = st.text_input("原訂單編號")
    target_date = st.date_input("新服務日期", value=None)
    if st.button("建立轉換資料", use_container_width=True):
        st.json(order_converter.convert({"source_order": source_order, "target_date": str(target_date or "")}))

else:
    step("2", "儲值金補價差")
    balance = st.number_input("儲值金餘額", min_value=0, value=0, step=100)
    need = st.number_input("本次服務金額", min_value=0, value=0, step=100)
    if st.button("計算補價差", use_container_width=True):
        diff = stored_value_makeup.calculate(int(balance), int(need))
        st.metric("需補價差", diff)

st.markdown("---")
st.caption("service-lemonsystem · unified feature menu")
