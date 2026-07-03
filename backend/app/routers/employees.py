from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Employee
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    designation: Optional[str] = None
    skill_level: str = "semi-skilled"
    shift_preference: str = "A"
    hourly_cost: float = 0

@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.is_active == True).all()

@router.post("/")
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = Employee(**emp.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp
