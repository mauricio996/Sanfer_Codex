from __future__ import annotations

from typing import Dict, List


def _bar(label: str, pct: float) -> str:
    width = max(1, min(100, int(pct)))
    return f"<div><strong>{label}</strong> {pct:.1f}%<div style='background:#eee;height:12px'><div style='width:{width}%;height:12px;background:#2E7D32'></div></div></div>"


def build_html_report(summary: Dict, channels: List[Dict], categories: List[Dict], ad_summary: Dict, alerts: List[Dict], recommendations: List[str], report_date: str) -> str:
    bars = "".join([
        _bar("Sessions", summary["pace_sessions_pct"]),
        _bar("Conversions", summary["pace_conversions_pct"]),
        _bar("Revenue", summary["pace_revenue_pct"]),
    ])
    channels_html = "".join(
        f"<tr><td>{c['channel']}</td><td>{c['sessions']:.0f}</td><td>{c['conversions']:.0f}</td><td>{c.get('cvr',0):.2%}</td></tr>" for c in channels
    )
    categories_html = "".join(
        f"<tr><td>{c['category']}</td><td>{c['transactions']:.0f}</td><td>{c['revenue']:.2f}</td><td>{c['role_badge']}</td></tr>" for c in categories
    )
    alerts_html = "".join(f"<li><b>{a.get('status')}</b> - {a.get('message', a.get('kpi'))}</li>" for a in alerts)
    recs_html = "".join(f"<li>{r}</li>" for r in recommendations)
    return f"""
    <html><body>
    <h2>San Fernando - Weekly Tracker</h2>
    <h3>1) KPI Summary</h3>
    <p>Sessions: {summary['sessions_mtd']:.0f} | Conversions: {summary['conversions_mtd']:.0f} | Revenue PEN: {summary['revenue_mtd']:.2f} | New users: {summary['new_users_mtd']:.0f}</p>
    <h3>2) Pace bars</h3>{bars}
    <h3>3) Channel ranking</h3><table border='1'><tr><th>Channel</th><th>Sessions</th><th>Conversions</th><th>CVR</th></tr>{channels_html}</table>
    <h3>4) Category performance</h3><table border='1'><tr><th>Category</th><th>Transactions</th><th>Revenue</th><th>Role</th></tr>{categories_html}</table>
    <h3>5) Ad spend summary</h3><p>Meta + Google spend: {ad_summary['total_spend']:.2f} | Cost/conv: {ad_summary['cost_per_conversion']:.2f}</p>
    <h3>6) Alerts</h3><ul>{alerts_html}</ul><h4>Top 3 actions</h4><ul>{recs_html}</ul>
    <hr/><small>Generado automáticamente — datos al {report_date}</small>
    </body></html>
    """
