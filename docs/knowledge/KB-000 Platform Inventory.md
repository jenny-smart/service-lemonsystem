# KB-000 平台盤點（Platform Inventory）

狀態：草稿
版本：0.1

## 目的

在開始整合與重構前，先完整盤點 Lemon Platform 現有資產，作為後續架構設計的依據。

## Repository 盤點

| Repository | 業務領域 | 狀態 | 未來策略 |
|---|---|---|---|
| service-lemonsystem | Service | 使用中 | 作為平台入口 |
| orders-system | Service | 使用中 | 逐步整合 |
| memo-system | Operations | 使用中 | 逐步整合 |
| tool-system | Tools | 使用中 | 整合為 Tool Center |
| salary-system | Finance | 使用中 | 整合為 Finance Center |

## 平台技術
- Streamlit
- Google Apps Script（GAS）
- Google Sheets
- Google Drive
- GitHub
- GitHub Actions

## 外部服務
- LINE
- Gmail
- Google Calendar

## 下一步
- KB-001 Repository 盤點
- KB-002 功能盤點
- KB-003 共用元件盤點