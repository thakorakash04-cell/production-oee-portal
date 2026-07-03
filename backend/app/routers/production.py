from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import ProductionEntry, DowntimeLog
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

router = APIRouter()

class DowntimeLogCreate(BaseModel):
    downtime_reason_id: int
    minutes_lost: float
    description: Optional[str] = None

class ProductionEntryCreate(BaseModel):
    entry_date: date
    shift_id: int
    product_id: int
    workstation_id: int
    planned_hours: float
    actual_hours: float
    planned_production: float
    actual_production: float
    good_pieces: float
    scrap: float = 0
    rework: float = 0
    manpower_planned: int
    manpower_actual: int
    supervisor_id: Optional[int] = None
    remarks: Optional[str] = None
    downtime_logs: List[DowntimeLogCreate] = []

class ProductionEntryResponse(BaseModel):
    id: int
    entry_date: date
    shift_id: int
    product_id: int
    workstation_id: int
    planned_hours: float
    actual_hours: float
    planned_production: float
    actual_production: float
    good_pieces: float
    scrap: float
    rework: float
    manpower_planned: int
    manpower_actual: int
    remarks: Optional[str]
    class Config:
        from_attributes = True

@router.post("/", response_model=ProductionEntryResponse)
def create_production_entry(entry: ProductionEntryCreate, db: Session = Depends(get_db)):
    db_entry = ProductionEntry(
        entry_date=entry.entry_date,
        shift_id=entry.shift_id,
        product_id=entry.product_id,
        workstation_id=entry.workstation_id,
        planned_hours=entry.planned_hours,
        actual_hours=entry.actual_hours,
        planned_production=entry.planned_production,
        actual_production=entry.actual_production,
        good_pieces=entry.good_pieces,
        scrap=entry.scrap,
        rework=entry.rework,
        manpower_planned=entry.manpower_planned,
        manpower_actual=entry.manpower_actual,
        supervisor_id=entry.supervisor_id,
        remarks=entry.remarks
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    for dl in entry.downtime_logs:
        log = DowntimeLog(
            production_entry_id=db_entry.id,
            downtime_reason_id=dl.downtime_reason_id,
            minutes_lost=dl.minutes_lost,
            description=dl.description
        )
        db.add(log)
    db.commit()
    return db_entry

@router.get("/")
def get_production_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    product_id: Optional[int] = None,
    shift_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    q = db.query(ProductionEntry)
    if start_date:
        q = q.filter(ProductionEntry.entry_date >= start_date)
    if end_date:
        q = q.filter(ProductionEntry.entry_date <= end_date)
    if product_id:
        q = q.filter(ProductionEntry.product_id == product_id)
    if shift_id:
        q = q.filter(ProductionEntry.shift_id == shift_id)
    entries = q.order_by(ProductionEntry.entry_date.desc()).limit(200).all()
    return entries

@router.get("/{entry_id}")
def get_production_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(ProductionEntry).filter(ProductionEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.delete("/{entry_id}")
def delete_production_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(ProductionEntry).filter(ProductionEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted"}
