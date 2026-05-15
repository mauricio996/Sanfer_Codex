from __future__ import annotations

from typing import Dict, List


def classify_pace(pct: float) -> str:
    if pct < 80:
        return "CRITICAL"
    if pct < 95:
        return "WARNING"
    if pct <= 110:
        return "ON_TRACK"
    return "AHEAD"


def evaluate_alerts(kpi_pace: Dict[str, float], channels: Dict, categories: Dict, prior_week_categories: Dict | None = None) -> List[Dict]:
    alerts = []
    for kpi, value in kpi_pace.items():
        status = classify_pace(value)
        alerts.append({"type": "kpi", "kpi": kpi, "pace_pct": value, "status": status})

    for name, data in channels.items():
        if data.get("sessions", 0) > 100 and data.get("conversions", 0) == 0:
            alerts.append({"type": "channel", "status": "WARNING", "message": f"{name} tiene >100 sesiones sin conversiones esta semana."})

    if prior_week_categories:
        for name, data in categories.items():
            if name == "Huevo":
                prev = prior_week_categories.get(name, {}).get("transactions", 0)
                curr = data.get("transactions", 0)
                if prev > 0 and curr < prev * 0.8:
                    alerts.append({"type": "category", "status": "CRITICAL", "message": "Huevo cae más de 20% vs semana previa."})
    return alerts


def top_recommendations(alerts: List[Dict]) -> List[str]:
    recs = []
    if any(a.get("status") == "CRITICAL" for a in alerts):
        recs.append("Reasignar presupuesto inmediatamente a campañas/canales de mejor CVR.")
    if any(a.get("type") == "channel" for a in alerts):
        recs.append("Revisar tracking, audiencias y landings en canales con sesiones sin conversiones.")
    if any(a.get("status") == "AHEAD" for a in alerts):
        recs.append("Evaluar reducción táctica de inversión y reservar excedente para semanas de menor demanda.")
    recs.append("Activar test A/B en creatividades y audiencias para sostener ritmo de conversiones.")
    return recs[:3]
