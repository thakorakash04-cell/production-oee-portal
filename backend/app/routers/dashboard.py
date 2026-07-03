from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.models import ProductionEntry, DowntimeLog, MonthlySchedule, CycleTime
from datetime import date, timedelta
from typing import Optional

router = APIRouter()

def calc_oee(entries):
    if not entries:
        return {"availability": 0, "performance": 0, "quality": 0, "oee": 0}
    total_planned = sum(e.planned_hours or 0 for e in entries)
    total_actual = sum(e.actual_hours or 0 for e in entries)
    total_produced = sum(e.actual_production or 0 for e in entries)
    total_good = sum(e.good_pieces or 0 for e in entries)
    # Availability
    availability = (total_actual / total_planned * 100) if total_planned > 0 else 0
    # Performance - using planned vs actual output
    total_planned_prod = sum(e.planned_production or 0 for e in entries)
    performance = (total_produced / total_planned_prod * 100) if total_planned_prod > 0 else 0
    # Quality
    quality = (total_good / total_produced * 100) if total_produced > 0 else 0
    # OEE
    oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
    return {
        "availability": round(availability, 2),
        "performance": round(performance, 2),
        "quality": round(quality, 2),
        "oee": round(oee, 2)
    }

@router.get("/summary")
def get_dashboard_summary(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    entries = db.query(ProductionEntry).filter(
        ProductionEntry.entry_date >= start_date,
        ProductionEntry.entry_date <= end_date
    ).all()
    oee_data = calc_oee(entries)
    total_planned = sum(e.planned_production or 0 for e in entries)
    total_actual = sum(e.actual_production or 0 for e in entries)
    total_good = sum(e.good_pieces or 0 for e in entries)
    total_scrap = sum(e.scrap or 0 for e in entries)
    return {
        "period": {"start": str(start_date), "end": str(end_date)},
        "oee": oee_data,
        "production": {
            "planned": total_planned,
            "actual": total_actual,
            "good": total_good,
            "scrap": total_scrap,
            "attainment_pct": round((total_actual / total_planned * 100) if total_planned > 0 else 0, 2)
        },
        "entries_count": len(entries)
    }

@router.get("/trend")
def get_oee_trend(
    days: int = Query(default=30),
    db: Session = Depends(get_db)
):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    entries = db.query(ProductionEntry).filter(
        ProductionEntry.entry_date >= start_date,
        ProductionEntry.entry_date <= end_date
    ).order_by(ProductionEntry.entry_date).all()
    # Group by date
    from collections import defaultdict
    daily = defaultdict(list)
    for e in entries:
        daily[str(e.entry_date)].append(e)
    trend = []
    for day, day_entries in sorted(daily.items()):
        oee = calc_oee(day_entries)
        trend.append({"date": day, **oee,
            "actual": sum(e.actual_production or 0 for e in day_entries),
            "planned": sum(e.planned_production or 0 for e in day_entries)
        })
    return {"trend": trend}

@router.get("/downtime-analysis")
def get_downtime_analysis(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    entries = db.query(ProductionEntry).filter(
        ProductionEntry.entry_date >= start_date,
        ProductionEntry.entry_date <= end_date
    ).all()
    entry_ids = [e.id for e in entries]
    logs = db.query(DowntimeLog).filter(
        DowntimeLog.production_entry_id.in_(entry_ids)
    ).all()
    from collections import defaultdict
    by_reason = defaultdict(float)
    for log in logs:
        reason_name = log.reason.name if log.reason else "Unknown"
        by_reason[reason_name] += log.minutes_lost or 0
    total_downtime = sum(by_reason.values())
    return {
        "total_downtime_minutes": round(total_downtime, 2),
        "breakdown": [
            {"reason": k, "minutes": round(v, 2), "pct": round(v/total_downtime*100 if total_downtime > 0 else 0, 2)}
            for k, v in sorted(by_reason.items(), key=lambda x: -x[1])
        ]
    }
