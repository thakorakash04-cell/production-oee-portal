from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import auth, products, workstations, machines, employees, shifts, schedules, production, downtime, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Production Monitoring & OEE Portal",
    description="Medical Device Manufacturing - OEE Dashboard API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(workstations.router, prefix="/api/v1/workstations", tags=["Workstations"])
app.include_router(machines.router, prefix="/api/v1/machines", tags=["Machines"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])
app.include_router(schedules.router, prefix="/api/v1/schedules", tags=["Schedules"])
app.include_router(production.router, prefix="/api/v1/production", tags=["Production"])
app.include_router(downtime.router, prefix="/api/v1/downtime", tags=["Downtime"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "OEE Portal API is running", "version": "2.0.0", "docs": "/docs"}
