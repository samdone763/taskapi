from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.sale import Sale, SaleItem, PaymentMethod
from app.models.product import Product
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/sales", tags=["Sales"])


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    payment_method: PaymentMethod = PaymentMethod.cash
    note: Optional[str] = None
    items: List[SaleItemCreate]


class SaleItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        orm_mode = True


class SaleOut(BaseModel):
    id: int
    total_amount: float
    payment_method: PaymentMethod
    note: Optional[str]
    owner_id: int
    created_at: datetime
    items: List[SaleItemOut]

    class Config:
        orm_mode = True


@router.post("/", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = 0.0
    sale_items = []

    for item in payload.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.owner_id == current_user.id,
            Product.is_active == True
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Bidhaa {item.product_id} haikupatikana")

        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock haitoshi kwa {product.name}")

        unit_price = product.selling_price
        total_price = unit_price * item.quantity
        total += total_price

        product.quantity -= item.quantity

        sale_items.append(SaleItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=total_price,
        ))

    sale = Sale(
        total_amount=total,
        payment_method=payload.payment_method,
        note=payload.note,
        owner_id=current_user.id,
    )
    db.add(sale)
    db.flush()

    for si in sale_items:
        si.sale_id = sale.id
        db.add(si)

    db.commit()
    db.refresh(sale)
    return sale


@router.get("/", response_model=List[SaleOut])
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Sale).filter(
        Sale.owner_id == current_user.id
    ).order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.owner_id == current_user.id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Muuzo haukupatikana")
    return sale
