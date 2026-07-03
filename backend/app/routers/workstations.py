from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Workstation
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class WorkstationCreate(BaseModel):
    code: str
    name: str
    department: Optional[str] = None
    capacity_per_shift: float = 0

@router.get("/")
def get_workstations(db: Session = Depends(get_db)):
    return db.query(Workstation).filter(Workstation.is_active == True).all()

@router.post("/")
def create_workstation(ws: WorkstationCreate, db: Session = Depends(get_db)):
    db_ws = Workstation(**ws.dict())
    db.add(db_ws)
    db.commit()
    db.refresh(db_ws)
    return db_ws

@router.delete("/{ws_id}")
def delete_workstation(ws_id: int, db: Session = Depends(get_db)):
    ws = db.query(Workstation).filter(Workstation.id == ws_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workstation not found")
    ws.is_active = False
    db.commit()
    return {"message": "Workstation deactivated"}
