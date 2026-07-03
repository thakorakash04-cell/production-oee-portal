from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import MonthlySchedule, CycleTime
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ScheduleCreate(BaseModel):
    year: int
    month: int
    product_id: int
    workstation_id: int
    target_quantity: float
    working_days: int = 26

@router.get("/")
def get_schedules(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(MonthlySchedule)
    if year:
        q = q.filter(MonthlySchedule.year == year)
    if month:
        q = q.filter(MonthlySchedule.month == month)
    return q.all()

@router.post("/")
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    daily_target = schedule.target_quantity / schedule.working_days
    # Calculate required manpower using cycle time if available
    ct = db.query(CycleTime).filter(
        CycleTime.product_id == schedule.product_id,
        CycleTime.workstation_id == schedule.workstation_id
    ).first()
    required_manpower = 1
    if ct and ct.ideal_output_per_hour > 0:
        hours_needed = schedule.target_quantity / ct.ideal_output_per_hour
        required_manpower = max(1, round(hours_needed / (schedule.working_days * 8)))
    db_schedule = MonthlySchedule(
        year=schedule.year,
        month=schedule.month,
        product_id=schedule.product_id,
        workstation_id=schedule.workstation_id,
        target_quantity=schedule.target_quantity,
        working_days=schedule.working_days,
        daily_target=daily_target,
        required_manpower=required_manpower
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.patch("/{schedule_id}/publish")
def publish_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(MonthlySchedule).filter(MonthlySchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule.status = "published"
    db.commit()
    return {"message": "Schedule published"}
