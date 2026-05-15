from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Dict, List

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

from . import config


class GA4Connector:
    def __init__(self, property_id: str | None = None, sa_path: str | None = None):
        self.property_id = property_id or config.GA4_PROPERTY_ID
        credentials = service_account.Credentials.from_service_account_file(
            sa_path or config.SERVICE_ACCOUNT_JSON_PATH
        )
        self.client = BetaAnalyticsDataClient(credentials=credentials)

    @staticmethod
    def _mtd_range() -> tuple[str, str]:
        today = dt.date.today()
        start = today.replace(day=1)
        end = today - dt.timedelta(days=1)
        return start.isoformat(), end.isoformat()

    def fetch_mtd_kpis_by_channel(self) -> Dict:
        start, end = self._mtd_range()
        req = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="sessions"), Metric(name="conversions"), Metric(name="newUsers")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        report = self.client.run_report(req)
        breakdown = defaultdict(lambda: {"sessions": 0.0, "conversions": 0.0, "new_users": 0.0})
        totals = {"sessions": 0.0, "conversions": 0.0, "new_users": 0.0}
        for row in report.rows:
            raw = row.dimension_values[0].value
            channel = config.GA4_CHANNEL_MAPPING.get(raw, "Other")
            sessions = float(row.metric_values[0].value)
            conv = float(row.metric_values[1].value)
            new_users = float(row.metric_values[2].value)
            breakdown[channel]["sessions"] += sessions
            breakdown[channel]["conversions"] += conv
            breakdown[channel]["new_users"] += new_users
            totals["sessions"] += sessions
            totals["conversions"] += conv
            totals["new_users"] += new_users
        return {"totals": totals, "channels": dict(breakdown)}

    def fetch_mtd_revenue_by_category(self) -> Dict:
        start, end = self._mtd_range()
        req = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[Dimension(name="itemCategory")],
            metrics=[Metric(name="transactions"), Metric(name="itemRevenue")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        report = self.client.run_report(req)
        categories = defaultdict(lambda: {"transactions": 0.0, "revenue": 0.0})
        total_revenue = 0.0
        for row in report.rows:
            raw_cat = (row.dimension_values[0].value or "").strip().lower()
            cat = config.GA4_ITEM_CATEGORY_MAP.get(raw_cat, "Other")
            tx = float(row.metric_values[0].value)
            rev = float(row.metric_values[1].value)
            categories[cat]["transactions"] += tx
            categories[cat]["revenue"] += rev
            total_revenue += rev
        return {"revenue": total_revenue, "categories": dict(categories), "period": {"start": start, "end": end}}
