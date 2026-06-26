# -*- coding: utf-8 -*-
"""清潔異動模組：車馬費 / 異動服務收款 / 異動服務退款。"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

BASE_URLS = {
    "prod": "https://backend.lemonclean.com.tw",
    "dev": "https://backend-dev.lemonclean.com.tw",
}
CURRENT_ENV = "prod"
BASE_URL = BASE_URLS[CURRENT_ENV]

SHEET_IDS = {
    "台北": "1bNcJuFuP--jdpNo2zJKOpvuq-5rSHW3LgGE8HEepf44",
    "台中": "1AlsgBL7uAooiU8hb0v-02J2MdBgDVJtGHgvD3U84hCM",
}
SHEET_GIDS = {"台北": 759897417, "台中": 759897417}
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
_GSPREAD_CLIENT = None

TAIWAN_PUBLIC_HOLIDAYS = {
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 2, 19), date(2026, 2, 20), date(2026, 2, 28), date(2026, 4, 4),
    date(2026, 4, 5), date(2026, 5, 1), date(2026, 6, 19), date(2026, 9, 25),
    date(2026, 10, 10), date(2026, 12, 25),
}

STATUS_PENDING_CHARGE = "待收款"
STATUS_PENDING_REFUND = "待退款"
STATUS_DONE_CHARGE = "已收款"
STATUS_DONE_REFUND = "已退款"
SYNC_STATUSES = {STATUS_PENDING_CHARGE, STATUS_PENDING_REFUND, STATUS_DONE_CHARGE, STATUS_DONE_REFUND}

TYPE_FARE = "車馬費發票"
TYPE_CHARGE = "異動服務收款"
TYPE_REFUND = "異動服務退款"
TYPE_COMPLAINT_REFUND = "客訴退款"
TYPE_DAMAGE_REFUND = "物損退款"

TIME_RATE_WEEKDAY = 600
TIME_RATE_WEEKEND = 700
TIME_RATE_DAY_TYPE_DIFF = 100


def set_env(env: str = "prod"):
    global CURRENT_ENV, BASE_URL
    env = (env or "prod").strip().lower()
    if env not in BASE_URLS:
        raise ValueError(f"不支援的環境：{env}")
    CURRENT_ENV = env
    BASE_URL = BASE_URLS[env]
    return BASE_URL


def get_base_url() -> str:
    return BASE_URL


def _log(ui_logger, msg: str):
    if ui_logger:
        ui_logger(str(msg))


def _get_gspread_client():
    global _GSPREAD_CLIENT
    if _GSPREAD_CLIENT is not None:
        return _GSPREAD_CLIENT
    if st is None:
        raise RuntimeError("找不到 streamlit，無法讀取 st.secrets")

    sa_info = None
    for key in ("GOOGLE_SERVICE_ACCOUNT", "gcp_service_account"):
        try:
            block = st.secrets.get(key, None)
        except Exception:
            block = None
        if not block:
            continue
        sa_info = json.loads(block) if isinstance(block, str) else dict(block)
        break
    if not sa_info:
        raise RuntimeError("找不到 Google 服務帳號憑證，請在 Streamlit secrets 設定 GOOGLE_SERVICE_ACCOUNT")
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    _GSPREAD_CLIENT = gspread.authorize(creds)
    return _GSPREAD_CLIENT


def get_worksheet(region: str, tab_name: str = "清潔異動"):
    if region not in SHEET_IDS:
        raise ValueError(f"不支援的地區：{region}")
    sh = _get_gspread_client().open_by_key(SHEET_IDS[region])
    gid = SHEET_GIDS.get(region)
    if gid is not None:
        for ws in sh.worksheets():
            if ws.id == gid:
                return ws
    try:
        return sh.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        return sh.get_worksheet(0)


def today_taipei_str(today: date | None = None) -> str:
    if today:
        return today.strftime("%Y/%m/%d")
    return datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y/%m/%d")


def money_int(value, default: int = 0) -> int:
    try:
        return int(round(float(value or 0)))
    except (TypeError, ValueError):
        return default


def parse_period_hours(period_text: str) -> float:
    m = re.search(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", period_text or "")
    if not m:
        return 0.0
    h1, m1, h2, m2 = map(int, m.groups())
    hours = ((h2 * 60 + m2) - (h1 * 60 + m1)) / 60
    if hours >= 6:
        hours -= 1
    return round(max(hours, 0), 2)


def is_workday(d: date) -> bool:
    return d.weekday() < 5 and d not in TAIWAN_PUBLIC_HOLIDAYS


def is_weekend_or_holiday(d: date) -> bool:
    return not is_workday(d)


def count_workdays_before(service_date: date, today: date | None = None) -> int:
    today = today or date.today()
    if service_date <= today:
        return 0
    days = 0
    d = today
    while d < service_date:
        if is_workday(d):
            days += 1
        d += timedelta(days=1)
    return days


def get_travel_fee(order: dict) -> int:
    return money_int((order or {}).get("travel_fee", 0))


def get_service_amount(order: dict) -> int:
    total = money_int((order or {}).get("total", 0))
    return max(total - get_travel_fee(order), 0)


def format_money(amount) -> str:
    try:
        return str(int(round(float(amount or 0))))
    except (TypeError, ValueError):
        return str(amount or "")


def format_hours(hours) -> str:
    try:
        value = float(hours or 0)
    except (TypeError, ValueError):
        return str(hours or "")
    if value.is_integer():
        return str(int(value))
    return str(value).rstrip("0").rstrip(".")


def change_timing_label(workdays: int) -> str:
    if workdays <= 0:
        return "服務當天異動"
    if workdays == 1:
        return "服務前1天異動"
    return f"服務前{workdays}個工作天異動"


def calc_fare(order: dict) -> int:
    return money_int(order.get("cleaner_count", 0)) * 100


def calc_change_fee(order: dict, service_date: date, change_person: int | None = None, today: date | None = None) -> dict:
    workdays = count_workdays_before(service_date, today=today)
    if workdays >= 4:
        tier = "free"
    elif workdays <= 1:
        tier = "near"
    else:
        tier = "far"
    note = change_timing_label(workdays)
    if order.get("payway") == "儲值金":
        hours = float(order.get("service_hours", 0) or 0)
        person = int(change_person or order.get("cleaner_count", 0) or 0)
        unit = (hours * person) / 2
        rate = 300 if tier == "near" else (200 if tier == "far" else 0)
        change_fee = round(unit * rate)
        calc_note = f"{note}，儲值金客：{hours}小時×{person}人÷2={unit}單位 × ${rate}/單位 = ${change_fee}" if tier != "free" else f"{note}，儲值金客：4個工作天以上，免收異動費 = $0"
        return {"workdays": workdays, "tier": tier, "change_fee": change_fee, "billing_units": unit, "rate_amount": rate, "rate_percent": None, "calc_note": calc_note}
    rate = 0.5 if tier == "near" else (0.3 if tier == "far" else 0)
    change_fee = round(money_int(order.get("total", 0)) * rate)
    calc_note = f"{note}，一般客：總金額{order.get('total', 0)} × {int(rate * 100)}% = ${change_fee}" if tier != "free" else f"{note}，一般客：4個工作天以上，免收異動費 = $0"
    return {"workdays": workdays, "tier": tier, "change_fee": change_fee, "billing_units": None, "rate_amount": None, "rate_percent": int(rate * 100), "calc_note": calc_note}


def calc_refund_amount(order: dict, change_fee: int) -> int:
    return max(get_service_amount(order) - money_int(change_fee), 0)


def calc_time_change_fee(service_date: date, hours: float, person: int) -> dict:
    weekend = is_weekend_or_holiday(service_date) if service_date else False
    rate = TIME_RATE_WEEKEND if weekend else TIME_RATE_WEEKDAY
    amount = round((hours or 0) * (person or 0) * rate)
    day_label = "週末/例假日" if weekend else "平日"
    return {"amount": amount, "rate": rate, "hours": hours, "person": person, "is_weekend": weekend, "calc_note": f"{day_label}：{hours}小時 × {person}人 × ${rate}/人時 = ${amount}"}


def calc_flat_person_hour_fee(hours: float, person: int, rate: int, label: str) -> dict:
    amount = round((hours or 0) * (person or 0) * rate)
    return {"amount": amount, "rate": rate, "hours": hours, "person": person, "calc_note": f"{label}：{hours}小時 × {person}人 × ${rate}/人時 = ${amount}"}


def format_service_datetime(service_date: date | None, period_text: str) -> str:
    if not service_date:
        return period_text or ""
    weekday = ["一", "二", "三", "四", "五", "六", "日"][service_date.weekday()]
    return f"{service_date.strftime('%Y-%m-%d')} ({weekday}) {period_text or ''}".strip()


def format_change_fee_j(order: dict, info: dict) -> str:
    timing = change_timing_label(info.get("workdays", 0))
    amount = format_money(info.get("change_fee"))
    if info.get("tier") == "free":
        return f"{timing}，免收異動費${amount}"
    if order.get("payway") == "儲值金":
        return f"{timing}，收異動費${format_money(info.get('rate_amount'))}*時數=${amount}"
    return f"{timing}，收{format_money(info.get('rate_percent'))}%異動費${amount}"


def build_fare_row(order: dict, service_date: date | None = None, today: date | None = None) -> dict:
    fare = calc_fare(order)
    return {"A": "清潔", "B": "待處理發票", "C": TYPE_FARE, "E": today_taipei_str(today), "F": "", "G": order.get("order_no", ""), "H": order.get("customer_name", ""), "I": format_service_datetime(service_date, order.get("period_text", "")), "J": f"車馬費 ${fare}", "_calc_amount": fare}


def build_charge_row(order: dict, change_fee_info: dict, service_note: str, customer_type: str = "一般", service_date: date | None = None, today: date | None = None) -> dict:
    return {"A": "清潔", "B": STATUS_PENDING_CHARGE, "C": TYPE_CHARGE, "E": today_taipei_str(today), "F": customer_type, "G": order.get("order_no", ""), "H": order.get("customer_name", ""), "I": format_service_datetime(service_date, order.get("period_text", "")), "J": format_change_fee_j(order, change_fee_info), "K": service_note or "", "M": "", "N": change_fee_info["change_fee"], "O": "", "_calc_amount": change_fee_info["change_fee"], "_calc_note": change_fee_info["calc_note"]}


def build_refund_row(order: dict, change_fee_info: dict, service_note: str, customer_type: str = "一般", service_date: date | None = None, today: date | None = None) -> dict:
    refund_amount = calc_refund_amount(order, change_fee_info["change_fee"])
    return {"A": "清潔", "B": STATUS_PENDING_REFUND, "C": TYPE_REFUND, "E": today_taipei_str(today), "F": customer_type, "G": order.get("order_no", ""), "H": order.get("customer_name", ""), "I": format_service_datetime(service_date, order.get("period_text", "")), "J": format_change_fee_j(order, change_fee_info), "K": service_note or "", "R": "信用卡" if order.get("payway") != "儲值金" else "儲值金", "S": refund_amount, "X": order.get("invoice_no", ""), "Y": "三聯" if order.get("carrier_type") == "三聯式" else "二聯", "_calc_amount": refund_amount, "_refund_amount": refund_amount, "_change_fee": change_fee_info.get("change_fee", 0), "_travel_fee": get_travel_fee(order), "_service_amount": get_service_amount(order), "_calc_note": change_fee_info["calc_note"]}


def build_time_change_row(order: dict, time_fee_info: dict, service_note: str, action: str, customer_type: str = "一般", service_date: date | None = None, today: date | None = None) -> dict:
    status = STATUS_PENDING_CHARGE if action in ("加時", "平日轉週末") else STATUS_PENDING_REFUND
    amount_col = "N" if status == STATUS_PENDING_CHARGE else "S"
    j = f"{action}{format_hours(time_fee_info.get('person'))}人{format_hours(time_fee_info.get('hours'))}小時，{'待收' if status == STATUS_PENDING_CHARGE else '待退'}服務費${format_money(time_fee_info.get('amount'))}"
    row = {"A": "清潔", "B": status, "C": TYPE_CHARGE if status == STATUS_PENDING_CHARGE else TYPE_REFUND, "E": today_taipei_str(today), "F": customer_type, "G": order.get("order_no", ""), "H": order.get("customer_name", ""), "I": format_service_datetime(service_date, order.get("period_text", "")), "J": j, "K": service_note or "", amount_col: time_fee_info["amount"], "_calc_amount": time_fee_info["amount"], "_calc_note": time_fee_info["calc_note"]}
    if status == STATUS_PENDING_REFUND:
        row.update({"R": "信用卡" if order.get("payway") != "儲值金" else "儲值金", "X": order.get("invoice_no", ""), "Y": "三聯" if order.get("carrier_type") == "三聯式" else "二聯"})
    return row


def build_manual_refund_row(order: dict, amount, refund_type_label: str, service_note: str, customer_type: str = "一般", service_date: date | None = None, today: date | None = None) -> dict:
    amount = round(amount or 0)
    j_value = f"{refund_type_label}，{service_note}，退費 ${amount}" if service_note else f"{refund_type_label}，退費 ${amount}"
    return {"A": "清潔", "B": STATUS_PENDING_REFUND, "C": refund_type_label, "E": today_taipei_str(today), "F": customer_type, "G": order.get("order_no", ""), "H": order.get("customer_name", ""), "I": format_service_datetime(service_date, order.get("period_text", "")), "J": j_value, "K": service_note or "", "R": "信用卡" if order.get("payway") != "儲值金" else "儲值金", "S": amount, "X": order.get("invoice_no", ""), "Y": "三聯" if order.get("carrier_type") == "三聯式" else "二聯", "_calc_amount": amount, "_calc_note": f"{refund_type_label}（人工輸入金額）= ${amount}"}


def _col_letter_to_index(letter: str) -> int:
    result = 0
    for ch in letter.strip().upper():
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result - 1


def _sheet_cell(row: list, letter: str) -> str:
    idx = _col_letter_to_index(letter)
    return str(row[idx]).strip() if len(row) > idx else ""


def append_rows_to_sheet(region: str, rows: list[dict], ui_logger=None):
    if not rows:
        return {"written": 0, "errors": [], "start_row": None}
    ws = get_worksheet(region)
    b_values = ws.col_values(2)
    last_data_row = len(b_values)
    while last_data_row > 0 and not str(b_values[last_data_row - 1]).strip():
        last_data_row -= 1
    start_row = last_data_row + 1
    col_letters = sorted({k for row in rows for k in row.keys() if not str(k).startswith("_") and k != "K"}, key=_col_letter_to_index)
    needed_rows = start_row + len(rows) - 1
    if needed_rows > ws.row_count:
        ws.add_rows(needed_rows - ws.row_count)

    written = 0
    errors = []
    for i, row in enumerate(rows):
        target_row = start_row + i
        try:
            for col in col_letters:
                if col in row and row[col] != "":
                    ws.update_acell(f"{col}{target_row}", row[col])
            written += 1
            _log(ui_logger, f"✅ 已寫入第 {target_row} 列：{row.get('G', '')}")
        except Exception as exc:
            errors.append(f"第 {target_row} 列（{row.get('G', '')}）寫入失敗：{exc}")
    return {"written": written, "errors": errors, "start_row": start_row}


def parse_sheet_row_spec(row_spec: str) -> set[int]:
    text = str(row_spec or "").strip()
    if not text:
        return set()
    rows = set()
    for part in re.split(r"[,，\s]+", text):
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            if start > end:
                start, end = end, start
            rows.update(range(start, end + 1))
        elif re.fullmatch(r"\d+", part):
            rows.add(int(part))
        else:
            raise ValueError(f"列號格式錯誤：{part}（支援：19、19,21、19-22）")
    return rows


def _row_kind(status: str) -> str:
    if status in (STATUS_PENDING_CHARGE, STATUS_DONE_CHARGE):
        return "charge"
    if status in (STATUS_PENDING_REFUND, STATUS_DONE_REFUND):
        return "refund"
    return ""


def _row_amount(row: list, status: str) -> str:
    if _row_kind(status) == "charge":
        return _sheet_cell(row, "N")
    if _row_kind(status) == "refund":
        return _sheet_cell(row, "S")
    return ""


def get_pending_rows(region: str, row_spec: str | None = None, ui_logger=None):
    wanted_rows = parse_sheet_row_spec(row_spec) if row_spec else set()
    ws = get_worksheet(region)
    all_values = ws.get_all_values()
    pending = []
    for row_no, row in enumerate(all_values[1:], start=2):
        if wanted_rows and row_no not in wanted_rows:
            continue
        status = _sheet_cell(row, "B")
        order_no = _sheet_cell(row, "G")
        if not order_no or status not in SYNC_STATUSES:
            continue
        amount = _row_amount(row, status)
        if not amount:
            continue
        kind = _row_kind(status)
        pending.append({
            "sheet_row": row_no,
            "kind": kind,
            "status": status,
            "order_no": order_no,
            "customer_name": _sheet_cell(row, "H"),
            "j_note": _sheet_cell(row, "J"),
            "k_note": _sheet_cell(row, "K"),
            "refund_invoice_type": _sheet_cell(row, "Y") if kind == "refund" else "",
            "amount": amount,
            "raw": row,
        })
    _log(ui_logger, f"掃描到 {len(pending)} 筆待回填資料" + (f"（指定列號：{row_spec}）" if row_spec else ""))
    return pending
