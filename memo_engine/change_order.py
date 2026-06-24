# -*- coding: utf-8 -*-
"""清潔異動模組：車馬費 / 異動服務收款 / 異動服務退款。"""

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

BASE_URLS = {
    "prod": "https://backend.lemonclean.com.tw",
    "dev": "https://backend-dev.lemonclean.com.tw",
}
CURRENT_ENV = "prod"
BASE_URL = BASE_URLS[CURRENT_ENV]

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
    return {"amount": amount, "rate": rate, "hours": hours, "person": person, "calc_note": f"{label}：{hours}小時 × {person}人 × ${rate}/人時 = {amount}"}


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
