from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Machine
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()

class MachineCreate(BaseModel):
    asset_code: str
    name: str
    workstation_id: int
    status: str = "active"
    maintenance_due: Optional[date] = None

@router.get("/")
def get_machines(db: Session = Depends(get_db)):
    return db.query(Machine).filter(Machine.is_active == True).all()

@router.post("/")
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    db_machine = Machine(**machine.dict())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

@router.patch("/{machine_id}/status")
def update_machine_status(machine_id: int, status: str, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    machine.status = status
    db.commit()
    return {"message": f"Machine status updated to {status}"}
