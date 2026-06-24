# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import date
import streamlit as st

from memo_engine import change_order


def render():
    st.subheader("🔄 服務異動")
    tab_calc, tab_sync = st.tabs(["異動試算 / 寫入 Sheet", "後台同步"])

    with tab_calc:
        st.markdown("##### 訂單資料")
        c1, c2, c3 = st.columns(3)
        with c1:
            region = st.selectbox("地區", ["台北", "台中"])
            order_no = st.text_input("訂單編號")
            customer_name = st.text_input("客戶姓名")
        with c2:
            service_date = st.date_input("服務日期", value=date.today())
            period_text = st.text_input("原服務時段", placeholder="09:00 - 13:00")
            cleaner_count = st.number_input("人數", min_value=1, value=1, step=1)
        with c3:
            service_hours = st.number_input("服務時數", min_value=0.0, value=4.0, step=0.5)
            total = st.number_input("訂單總金額", min_value=0, value=0, step=100)
            travel_fee = st.number_input("原車馬費", min_value=0, value=0, step=100)

        c4, c5, c6 = st.columns(3)
        with c4:
            payway = st.selectbox("付款類型", ["非儲值金", "儲值金"])
        with c5:
            invoice_no = st.text_input("原發票號碼")
        with c6:
            carrier_type = st.selectbox("發票類型", ["二聯式", "三聯式"])

        scenario = st.radio(
            "異動類型",
            ["車馬費發票", "異動服務收款", "異動服務退款", "加時", "減時", "平日轉週末", "週末轉平日", "客訴退款", "物損退款"],
        )
        service_note = st.text_area("服務 / 財務備註", height=100)
        customer_type = st.selectbox("客戶類別", ["一般", "儲值金", "其他"])

        extra_hours = 0.0
        extra_person = 1
        manual_amount = 0
        if scenario in ["加時", "減時", "平日轉週末", "週末轉平日"]:
            a, b = st.columns(2)
            with a:
                extra_hours = st.number_input("異動時數", min_value=0.0, value=1.0, step=0.5)
            with b:
                extra_person = st.number_input("異動人數", min_value=1, value=1, step=1)
        if scenario in ["客訴退款", "物損退款"]:
            manual_amount = st.number_input("退款金額", min_value=0, value=0, step=100)

        order = {
            "order_no": order_no,
            "customer_name": customer_name,
            "service_date": service_date,
            "period_text": period_text,
            "total": int(total or 0),
            "travel_fee": int(travel_fee or 0),
            "service_amount": max(int(total or 0) - int(travel_fee or 0), 0),
            "cleaner_count": int(cleaner_count or 0),
            "service_hours": float(service_hours or 0),
            "payway": payway,
            "invoice_no": invoice_no,
            "carrier_type": carrier_type,
        }

        if st.button("產生試算", use_container_width=True):
            try:
                rows = _build_rows(scenario, order, service_date, service_note, customer_type, extra_hours, int(extra_person), manual_amount)
                st.session_state["service_change_preview_rows"] = rows
            except Exception as exc:
                st.error(f"試算失敗：{exc}")

        rows = st.session_state.get("service_change_preview_rows", [])
        if rows:
            st.markdown("##### 預覽")
            st.dataframe([{k: v for k, v in row.items() if not str(k).startswith("_")} for row in rows], use_container_width=True)
            with st.expander("計算依據"):
                for row in rows:
                    if row.get("_calc_note"):
                        st.write(row["_calc_note"])
            if st.button("寫入清潔異動工作表", use_container_width=True):
                try:
                    result = change_order.append_rows_to_sheet(region, rows, ui_logger=st.write)
                    st.success(f"已寫入 {result.get('written', 0)} 筆，起始列：{result.get('start_row')}")
                    if result.get("errors"):
                        st.warning("\n".join(result["errors"]))
                except Exception as exc:
                    st.error(f"寫入失敗：{exc}")

    with tab_sync:
        st.markdown("##### 後台同步")
        st.info("此頁先完成待回填列掃描；實際回填需接入共用登入 session。")
        region2 = st.selectbox("同步地區", ["台北", "台中"], key="sync_region")
        row_spec = st.text_input("指定列號", placeholder="19 或 19,21 或 19-22")
        if st.button("掃描待回填列", use_container_width=True):
            try:
                pending = change_order.get_pending_rows(region2, row_spec=row_spec, ui_logger=st.write)
                st.session_state["service_change_pending_rows"] = pending
                st.success(f"掃描到 {len(pending)} 筆")
            except Exception as exc:
                st.error(f"掃描失敗：{exc}")
        pending = st.session_state.get("service_change_pending_rows", [])
        if pending:
            st.dataframe([
                {"列號": x.get("sheet_row"), "狀態": x.get("status"), "訂單": x.get("order_no"), "客戶": x.get("customer_name"), "金額": x.get("amount")}
                for x in pending
            ], use_container_width=True)


def _build_rows(scenario, order, service_date, service_note, customer_type, extra_hours, extra_person, manual_amount):
    if scenario == "車馬費發票":
        return [change_order.build_fare_row(order, service_date=service_date)]
    if scenario == "異動服務收款":
        info = change_order.calc_change_fee(order, service_date)
        return [change_order.build_charge_row(order, info, service_note, customer_type, service_date=service_date)]
    if scenario == "異動服務退款":
        info = change_order.calc_change_fee(order, service_date)
        return [change_order.build_refund_row(order, info, service_note, customer_type, service_date=service_date)]
    if scenario == "加時":
        info = change_order.calc_time_change_fee(service_date, extra_hours, extra_person)
        return [change_order.build_time_change_row(order, info, service_note, "加時", customer_type, service_date=service_date)]
    if scenario == "減時":
        info = change_order.calc_time_change_fee(service_date, extra_hours, extra_person)
        return [change_order.build_time_change_row(order, info, service_note, "減時", customer_type, service_date=service_date)]
    if scenario == "平日轉週末":
        info = change_order.calc_flat_person_hour_fee(extra_hours, extra_person, getattr(change_order, "TIME_RATE_DAY_TYPE_DIFF", 100), "平日轉週末差額")
        return [change_order.build_time_change_row(order, info, service_note, "平日轉週末", customer_type, service_date=service_date)]
    if scenario == "週末轉平日":
        info = change_order.calc_flat_person_hour_fee(extra_hours, extra_person, getattr(change_order, "TIME_RATE_DAY_TYPE_DIFF", 100), "週末轉平日差額")
        return [change_order.build_time_change_row(order, info, service_note, "週末轉平日", customer_type, service_date=service_date)]
    if scenario == "客訴退款":
        return [change_order.build_manual_refund_row(order, manual_amount, change_order.TYPE_COMPLAINT_REFUND, service_note, customer_type, service_date=service_date)]
    return [change_order.build_manual_refund_row(order, manual_amount, change_order.TYPE_DAMAGE_REFUND, service_note, customer_type, service_date=service_date)]
