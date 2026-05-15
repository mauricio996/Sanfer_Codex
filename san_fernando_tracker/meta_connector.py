from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Dict

import requests

from . import config


class MetaConnector:
    API_VERSION = "v20.0"

    @staticmethod
    def _week_range() -> tuple[str, str]:
        today = dt.date.today()
        monday = today - dt.timedelta(days=today.weekday())
        return monday.isoformat(), today.isoformat()

    def fetch_weekly_campaign_metrics(self) -> Dict:
        since, until = self._week_range()
        url = f"https://graph.facebook.com/{self.API_VERSION}/{config.META_AD_ACCOUNT_ID}/insights"
        params = {
            "access_token": config.META_ACCESS_TOKEN,
            "level": "campaign",
            "fields": "campaign_name,objective,spend,impressions,clicks,actions",
            "time_range": f'{{"since":"{since}","until":"{until}"}}',
        }
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json().get("data", [])

        by_objective = defaultdict(lambda: {"spend": 0.0, "impressions": 0.0, "clicks": 0.0, "conversions": 0.0})
        campaigns = []
        for row in data:
            actions = row.get("actions", [])
            conversions = sum(float(a.get("value", 0.0)) for a in actions if a.get("action_type") in {"purchase", "onsite_conversion.purchase"})
            objective = config.META_OBJECTIVE_MAP.get(row.get("objective", ""), "conversion")
            metric = {
                "campaign": row.get("campaign_name", "Unknown"),
                "objective": objective,
                "spend": float(row.get("spend", 0.0)),
                "impressions": float(row.get("impressions", 0.0)),
                "clicks": float(row.get("clicks", 0.0)),
                "conversions": conversions,
            }
            campaigns.append(metric)
            for k in ("spend", "impressions", "clicks", "conversions"):
                by_objective[objective][k] += metric[k]
        return {"period": {"since": since, "until": until}, "campaigns": campaigns, "objective_breakdown": dict(by_objective)}
