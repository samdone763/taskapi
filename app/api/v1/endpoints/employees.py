from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.employee import Employee, EmployeeRole
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["Employees"])


class EmployeeCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    role: EmployeeRole = EmployeeRole.other
    salary: float


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[EmployeeRole] = None
    salary: Optional[float] = None
    is_active: Optional[bool] = None


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    phone: Optional[str]
    role: EmployeeRole
    salary: float
    is_active: bool
    owner_id: int
    joined_at: datetime

    class Config:
        orm_mode = True


@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = Employee(**payload.dict(), owner_id=current_user.id)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/", response_model=List[EmployeeOut])
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Employee).filter(
        Employee.owner_id == current_user.id,
        Employee.is_active == True
    ).offset(skip).limit(limit).all()


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.owner_id == current_user.id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Mfanyakazi hakupatikana")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.owner_id == current_user.id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Mfanyakazi hakupatikana")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.owner_id == current_user.id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Mfanyakazi hakupatikana")
    employee.is_active = False
    db.commit()
