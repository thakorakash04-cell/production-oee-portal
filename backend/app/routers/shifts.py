from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Shift
from pydantic import BaseModel

router = APIRouter()

class ShiftCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    planned_hours: float = 8.0

@router.get("/")
def get_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()

@router.post("/")
def create_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    db_shift = Shift(**shift.dict())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift
