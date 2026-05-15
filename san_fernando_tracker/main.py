from __future__ import annotations

import calendar
import datetime as dt
import logging
from email.mime.text import MIMEText
from typing import Dict

from . import config
from .alerts import evaluate_alerts, top_recommendations
from .bigquery import BigQueryClient
from .ga4_connector import GA4Connector
from .gads_connector import GoogleAdsConnector
from .meta_connector import MetaConnector
from .report import build_html_report

logging.basicConfig(level=logging.INFO)


def compute_summary(totals: Dict, revenue: float) -> Dict:
    today = dt.date.today()
    days_elapsed = today.day - 1
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    goals = config.MONTHLY_TARGETS
    pace_sessions = 100 * totals["sessions"] / (goals["sessions"] * days_elapsed / days_in_month)
    pace_conv = 100 * totals["conversions"] / (goals["conversions"] * days_elapsed / days_in_month)
    pace_rev = 100 * revenue / (goals["revenue"] * days_elapsed / days_in_month)
    return {
        "run_date": today.isoformat(),
        "days_elapsed": days_elapsed,
        "days_in_month": days_in_month,
        "sessions_mtd": totals["sessions"],
        "conversions_mtd": totals["conversions"],
        "new_users_mtd": totals["new_users"],
        "revenue_mtd": revenue,
        "sessions_goal": goals["sessions"],
        "conversions_goal": goals["conversions"],
        "new_users_goal": goals["new_users"],
        "revenue_goal": goals["revenue"],
        "pace_sessions_pct": pace_sessions,
        "pace_conversions_pct": pace_conv,
        "pace_revenue_pct": pace_rev,
        "projected_sessions": totals["sessions"] / days_elapsed * days_in_month,
        "projected_conversions": totals["conversions"] / days_elapsed * days_in_month,
        "projected_revenue": revenue / days_elapsed * days_in_month,
    }


def run_pipeline() -> None:
    errors = []
    ga_data, cat_data, meta_data, gads_data = {}, {}, {}, {}

    try:
        ga = GA4Connector()
        ga_data = ga.fetch_mtd_kpis_by_channel()
        cat_data = ga.fetch_mtd_revenue_by_category()
    except Exception as e:
        logging.exception("GA4 failed")
        errors.append(f"GA4: {e}")

    try:
        meta_data = MetaConnector().fetch_weekly_campaign_metrics()
    except Exception as e:
        logging.exception("Meta failed")
        errors.append(f"Meta: {e}")

    try:
        gads_data = GoogleAdsConnector().fetch_weekly_campaign_metrics()
    except Exception as e:
        logging.exception("Google Ads failed")
        errors.append(f"Google Ads: {e}")

    totals = ga_data.get("totals", {"sessions": 0, "conversions": 0, "new_users": 0})
    revenue = cat_data.get("revenue", 0.0)
    summary = compute_summary(totals, revenue)

    channels = []
    for ch, vals in ga_data.get("channels", {}).items():
        cvr = vals["conversions"] / vals["sessions"] if vals["sessions"] else 0
        channels.append({"channel": ch, **vals, "cvr": cvr})
    channels.sort(key=lambda x: x["conversions"], reverse=True)

    categories = []
    for cat, vals in cat_data.get("categories", {}).items():
        role = config.CATEGORY_ROLES.get(cat, "other")
        badge = "Adquisición" if role == "acquisition" else "Retención"
        categories.append({"category": cat, **vals, "role_badge": badge})

    alerts = evaluate_alerts(
        {
            "sessions": summary["pace_sessions_pct"],
            "conversions": summary["pace_conversions_pct"],
            "revenue": summary["pace_revenue_pct"],
        },
        ga_data.get("channels", {}),
        cat_data.get("categories", {}),
    )
    recommendations = top_recommendations(alerts)

    meta_spend = sum(c.get("spend", 0.0) for c in meta_data.get("campaigns", []))
    gads_spend = sum(c.get("spend", 0.0) for c in gads_data.get("campaigns", []))
    paid_conv = sum(c.get("conversions", 0.0) for c in meta_data.get("campaigns", [])) + sum(c.get("conversions", 0.0) for c in gads_data.get("campaigns", []))
    ad_summary = {"total_spend": meta_spend + gads_spend, "cost_per_conversion": (meta_spend + gads_spend) / paid_conv if paid_conv else 0}

    summary["channel_breakdown"] = ga_data.get("channels", {})
    summary["category_breakdown"] = cat_data.get("categories", {})

    try:
        BigQueryClient().insert_weekly_row(summary)
    except Exception as e:
        logging.exception("BigQuery failed")
        errors.append(f"BigQuery: {e}")

    html = build_html_report(summary, channels, categories, ad_summary, alerts, recommendations, dt.date.today().isoformat())
    if errors:
        html = f"<p><b>Fuentes con error:</b> {' | '.join(errors)}</p>" + html

    msg = MIMEText(html, "html")
    week_n = dt.date.today().isocalendar().week
    msg["Subject"] = f"[San Fernando] Semana {week_n} — Revenue al {summary['pace_revenue_pct']:.1f}% del pace"
    msg["From"] = config.GMAIL_SENDER
    msg["To"] = ", ".join(config.GMAIL_RECIPIENTS)

    logging.info("Report generated. Plug Gmail API/SMTP send function here.")
    print(msg.as_string()[:1000])


if __name__ == "__main__":
    run_pipeline()
