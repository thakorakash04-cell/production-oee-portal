from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import DowntimeReason, DowntimeLog
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class DowntimeReasonCreate(BaseModel):
    code: str
    name: str
    category: str

@router.get("/reasons")
def get_downtime_reasons(db: Session = Depends(get_db)):
    return db.query(DowntimeReason).all()

@router.post("/reasons")
def create_downtime_reason(reason: DowntimeReasonCreate, db: Session = Depends(get_db)):
    db_reason = DowntimeReason(**reason.dict())
    db.add(db_reason)
    db.commit()
    db.refresh(db_reason)
    return db_reason

@router.get("/logs")
def get_downtime_logs(production_entry_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(DowntimeLog)
    if production_entry_id:
        q = q.filter(DowntimeLog.production_entry_id == production_entry_id)
    return q.all()
