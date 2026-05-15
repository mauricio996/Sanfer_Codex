from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Dict

from google.ads.googleads.client import GoogleAdsClient

from . import config


class GoogleAdsConnector:
    def __init__(self):
        self.client = GoogleAdsClient.load_from_dict(
            {
                "developer_token": config.GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": config.GOOGLE_ADS_CLIENT_ID,
                "client_secret": config.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": config.GOOGLE_ADS_REFRESH_TOKEN,
                "use_proto_plus": True,
                "login_customer_id": config.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
            }
        )

    @staticmethod
    def _week_range() -> tuple[str, str]:
        today = dt.date.today()
        monday = today - dt.timedelta(days=today.weekday())
        return monday.isoformat(), today.isoformat()

    def fetch_weekly_campaign_metrics(self) -> Dict:
        since, until = self._week_range()
        service = self.client.get_service("GoogleAdsService")
        query = f"""
            SELECT campaign.name, campaign.advertising_channel_type,
                   metrics.cost_micros, metrics.clicks, metrics.conversions
            FROM campaign
            WHERE segments.date BETWEEN '{since}' AND '{until}'
        """
        rows = service.search(customer_id=config.GOOGLE_ADS_CUSTOMER_ID, query=query)
        by_type = defaultdict(lambda: {"spend": 0.0, "clicks": 0.0, "conversions": 0.0})
        campaigns = []
        for row in rows:
            ctype = config.GOOGLE_ADS_TYPE_MAP.get(row.campaign.advertising_channel_type.name, "Other")
            metric = {
                "campaign": row.campaign.name,
                "type": ctype,
                "spend": row.metrics.cost_micros / 1_000_000,
                "clicks": float(row.metrics.clicks),
                "conversions": float(row.metrics.conversions),
            }
            campaigns.append(metric)
            for k in ("spend", "clicks", "conversions"):
                by_type[ctype][k] += metric[k]
        return {"period": {"since": since, "until": until}, "campaigns": campaigns, "type_breakdown": dict(by_type)}
