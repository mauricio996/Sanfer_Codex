from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import os

# --- Credentials / auth ---
SERVICE_ACCOUNT_JSON_PATH = os.getenv("SF_SERVICE_ACCOUNT_JSON_PATH", "./service_account.json")
BIGQUERY_PROJECT_ID = os.getenv("SF_BQ_PROJECT_ID", "your-gcp-project")
BIGQUERY_DATASET = os.getenv("SF_BQ_DATASET", "san_fernando")
BIGQUERY_TABLE = os.getenv("SF_BQ_TABLE", "weekly_tracker")

GA4_PROPERTY_ID = os.getenv("SF_GA4_PROPERTY_ID", "123456789")

META_ACCESS_TOKEN = os.getenv("SF_META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.getenv("SF_META_AD_ACCOUNT_ID", "act_000000000")

GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("SF_GADS_DEVELOPER_TOKEN", "")
GOOGLE_ADS_CLIENT_ID = os.getenv("SF_GADS_CLIENT_ID", "")
GOOGLE_ADS_CLIENT_SECRET = os.getenv("SF_GADS_CLIENT_SECRET", "")
GOOGLE_ADS_REFRESH_TOKEN = os.getenv("SF_GADS_REFRESH_TOKEN", "")
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.getenv("SF_GADS_LOGIN_CUSTOMER_ID", "")
GOOGLE_ADS_CUSTOMER_ID = os.getenv("SF_GADS_CUSTOMER_ID", "")

# Gmail/SMTP
EMAIL_MODE = os.getenv("SF_EMAIL_MODE", "gmail_api")  # gmail_api | smtp
GMAIL_SENDER = os.getenv("SF_GMAIL_SENDER", "reportes@sanfernando.pe")
GMAIL_RECIPIENTS = os.getenv("SF_GMAIL_RECIPIENTS", "marketing@sanfernando.pe").split(",")
SMTP_HOST = os.getenv("SF_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SF_SMTP_PORT", "587"))
SMTP_USER = os.getenv("SF_SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SF_SMTP_PASSWORD", "")

TIMEZONE = "America/Lima"

# Monthly targets (update every month)
MONTHLY_TARGETS: Dict[str, float] = {
    "sessions": 600_000,
    "conversions": 12_000,
    "new_users": 170_000,
    "revenue": 2_200_000.0,  # PEN
}

CHANNEL_GROUPS: List[str] = [
    "Organic Search",
    "Paid Search",
    "Paid Social",
    "Email",
    "Direct",
    "WhatsApp",
    "Other",
]

CATEGORY_ROLES = {
    "Pollo": "retention",
    "Pavo": "retention",
    "Huevo": "acquisition",
}

GA4_CHANNEL_MAPPING = {
    "Organic Search": "Organic Search",
    "Paid Search": "Paid Search",
    "Paid Social": "Paid Social",
    "Email": "Email",
    "Direct": "Direct",
    "WhatsApp": "WhatsApp",
}

GA4_ITEM_CATEGORY_MAP = {
    "pollo": "Pollo",
    "pavo": "Pavo",
    "huevo": "Huevo",
}

META_OBJECTIVE_MAP = {
    "OUTCOME_AWARENESS": "awareness",
    "OUTCOME_TRAFFIC": "awareness",
    "OUTCOME_ENGAGEMENT": "awareness",
    "OUTCOME_LEADS": "conversion",
    "OUTCOME_SALES": "conversion",
}

GOOGLE_ADS_TYPE_MAP = {
    "SEARCH": "Search",
    "PERFORMANCE_MAX": "PMAX",
    "DISPLAY": "Remarketing",
}
