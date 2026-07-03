from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="supervisor")  # plant_manager, engineer, supervisor, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(100))
    uom = Column(String(20), default="PCS")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cycle_times = relationship("CycleTime", back_populates="product")
    schedules = relationship("MonthlySchedule", back_populates="product")

class Workstation(Base):
    __tablename__ = "workstations"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)
    name = Column(String(150), nullable=False)
    department = Column(String(100))
    capacity_per_shift = Column(Float, default=0)
    is_active = Column(Boolean, default=True)

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True)
    name = Column(String(150), nullable=False)
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    status = Column(String(30), default="active")  # active, maintenance, breakdown
    maintenance_due = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    workstation = relationship("Workstation")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True)
    name = Column(String(150), nullable=False)
    designation = Column(String(100))
    skill_level = Column(String(30), default="semi-skilled")  # skilled, semi-skilled, unskilled
    shift_preference = Column(String(10), default="A")
    hourly_cost = Column(Float, default=0)
    is_active = Column(Boolean, default=True)

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True)  # Shift A, Shift B, Shift C
    start_time = Column(String(10))
    end_time = Column(String(10))
    planned_hours = Column(Float, default=8.0)

class CycleTime(Base):
    __tablename__ = "cycle_times"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    standard_cycle_time = Column(Float)  # seconds per unit
    ideal_output_per_hour = Column(Float)
    product = relationship("Product", back_populates="cycle_times")
    workstation = relationship("Workstation")

class MonthlySchedule(Base):
    __tablename__ = "monthly_schedules"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    month = Column(Integer)
    product_id = Column(Integer, ForeignKey("products.id"))
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    target_quantity = Column(Float)
    working_days = Column(Integer, default=26)
    daily_target = Column(Float)
    required_manpower = Column(Integer)
    status = Column(String(20), default="draft")  # draft, published
    product = relationship("Product", back_populates="schedules")
    workstation = relationship("Workstation")

class DowntimeReason(Base):
    __tablename__ = "downtime_reasons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True)
    name = Column(String(150))
    category = Column(String(50))  # breakdown, material, manpower, planned, setup

class ProductionEntry(Base):
    __tablename__ = "production_entries"
    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(Date, nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    workstation_id = Column(Integer, ForeignKey("workstations.id"))
    planned_hours = Column(Float)
    actual_hours = Column(Float)
    planned_production = Column(Float)
    actual_production = Column(Float)
    good_pieces = Column(Float)
    scrap = Column(Float, default=0)
    rework = Column(Float, default=0)
    manpower_planned = Column(Integer)
    manpower_actual = Column(Integer)
    supervisor_id = Column(Integer, ForeignKey("users.id"))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    shift = relationship("Shift")
    product = relationship("Product")
    workstation = relationship("Workstation")
    supervisor = relationship("User")

class DowntimeLog(Base):
    __tablename__ = "downtime_logs"
    id = Column(Integer, primary_key=True, index=True)
    production_entry_id = Column(Integer, ForeignKey("production_entries.id"))
    downtime_reason_id = Column(Integer, ForeignKey("downtime_reasons.id"))
    minutes_lost = Column(Float)
    description = Column(Text)
    production_entry = relationship("ProductionEntry")
    reason = relationship("DowntimeReason")
