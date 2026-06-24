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
.hero { background:linear-gradient(135deg,#FFFDF5 0%,#FFFBEA 100%); border:1.5px solid var(--lemon-mid); border-radius:var(--radius); padding:2.1rem 2.6rem; margin-bottom:2.2rem; display:flex; align-items:center; gap:1.3rem; }
</style>
""", unsafe_allow_html=True)
MEMO_APP_URL = "https://memo-lemon-system.streamlit.app/"
ORDERS_APP_URL = "https://orders-lemon-system.streamlit.app/"
st.title('檸檬營運自動化工具')
section = st.selectbox('功能',['📋 客服 / Memo 系統','🧾 快速訂單系統'])
if section == '📋 客服 / Memo 系統':
    st.link_button('開啟 Memo 系統', MEMO_APP_URL)
else:
    st.link_button('開啟 快速訂單系統', ORDERS_APP_URL)
