from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Product, CycleTime, Workstation
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProductCreate(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    uom: str = "PCS"

class CycleTimeCreate(BaseModel):
    product_id: int
    workstation_id: int
    standard_cycle_time: float
    ideal_output_per_hour: float

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).all()

@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.code == product.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated"}

@router.post("/cycle-times/")
def create_cycle_time(ct: CycleTimeCreate, db: Session = Depends(get_db)):
    db_ct = CycleTime(**ct.dict())
    db.add(db_ct)
    db.commit()
    db.refresh(db_ct)
    return db_ct

@router.get("/cycle-times/all")
def get_all_cycle_times(db: Session = Depends(get_db)):
    return db.query(CycleTime).all()
