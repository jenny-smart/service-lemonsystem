# -*- coding: utf-8 -*-
"""Runtime helpers for service change page.

This module keeps login and purchase lookup separate from the calculation engine.
"""

from __future__ import annotations

import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from memo_engine import change_order

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}


def login(env_name: str, email: str, password: str) -> requests.Session:
    base_url = change_order.set_env(env_name)
    login_url = f"{base_url}/login"
    purchase_url = f"{base_url}/purchase"

    if not email or not password:
        raise RuntimeError("請輸入後台帳號與密碼")

    session = requests.Session()
    session.headers.update(HEADERS)

    resp = session.get(login_url, allow_redirects=True, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    token_el = soup.select_one('input[name="_token"]')
    if not token_el:
        raise RuntimeError("登入頁找不到 _token")
    token = token_el.get("value", "")

    resp = session.post(
        login_url,
        data={"_token": token, "email": email, "password": password},
        allow_redirects=True,
        timeout=20,
    )
    resp.raise_for_status()

    check = session.get(purchase_url, allow_redirects=True, timeout=20)
    check.raise_for_status()
    if "/login" in check.url:
        raise RuntimeError("登入失敗，請確認帳密")
    return session


def extract_service_date(text: str):
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text or "")
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    try:
        return date(y, mo, d)
    except ValueError:
        return None


def parse_period_hours(period_text: str) -> float:
    return change_order.parse_period_hours(period_text)


def parse_order_row(row) -> dict | None:
    checkbox = row.select_one('input[name="purchase_id[]"]')
    purchase_id = checkbox.get("value", "") if checkbox else ""

    order_no = ""
    label = row.select_one("td label")
    if label:
        m = re.search(r"(?:LC|TT)\d+", label.get_text(" ", strip=True))
        order_no = m.group(0) if m else label.get_text(" ", strip=True).split()[-1]
    else:
        m = re.search(r"(?:LC|TT)\d+", row.get_text(" ", strip=True))
        order_no = m.group(0) if m else ""
    if not order_no:
        return None

    name_tag = row.select_one('a[href*="/member?keyword"]')
    customer_name = name_tag.get_text(strip=True) if name_tag else ""

    tds = row.select("td")
    date_cell = tds[2] if len(tds) > 2 else None
    date_text = date_cell.get_text("\n", strip=True) if date_cell else ""
    period_match = re.search(r"\d{2}:\d{2}\s*-\s*\d{2}:\d{2}", date_text)
    period_text = period_match.group(0) if period_match else ""
    cleaner_count = len(date_cell.select('a[href*="schedule/edit"]')) if date_cell else 0
    service_date = extract_service_date(date_text)

    pay_cell = tds[3] if len(tds) > 3 else None
    pay_text = pay_cell.get_text("\n", strip=True) if pay_cell else ""

    total_match = re.search(r"總金額[：:]\s*([\d,]+)", pay_text)
    total = int(total_match.group(1).replace(",", "")) if total_match else 0
    travel_match = re.search(r"車馬費[：:]\s*([\d,]+)", pay_text)
    travel_fee = int(travel_match.group(1).replace(",", "")) if travel_match else 0
    invoice_match = re.search(r"發票[：:]\s*([A-Z0-9]+)", pay_text)

    return {
        "purchase_id": purchase_id,
        "order_no": order_no,
        "customer_name": customer_name,
        "service_date": service_date,
        "period_text": period_text,
        "service_hours": parse_period_hours(period_text),
        "cleaner_count": cleaner_count or 1,
        "total": total,
        "travel_fee": travel_fee,
        "service_amount": max(total - travel_fee, 0),
        "payway": "儲值金" if "儲值金" in pay_text else "非儲值金",
        "invoice_no": invoice_match.group(1) if invoice_match else "",
        "carrier_type": "三聯式" if "統編" in pay_text or "三聯" in pay_text else "二聯式",
        "raw_date_cell": date_text,
        "pay_status_text": pay_text,
        "is_paid": ("已付款" in pay_text) and ("未付款" not in pay_text),
    }


def fetch_order_basic(session: requests.Session, keyword: str, by: str = "orderNo") -> dict | None:
    if not keyword:
        raise RuntimeError("請輸入訂單編號或電話")
    base_url = change_order.get_base_url()
    resp = session.get(f"{base_url}/purchase", params={by: keyword}, allow_redirects=True, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    row = soup.select_one("table tbody tr")
    if not row:
        return None
    return parse_order_row(row)
