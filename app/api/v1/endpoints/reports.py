from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.sale import Sale, SaleItem
from app.models.expense import Expense
from app.models.product import Product
from app.models.user import User
from app.core.security import get_current_user
from datetime import datetime, date

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.owner_id == current_user.id
    ).scalar() or 0.0

    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.owner_id == current_user.id
    ).scalar() or 0.0

    total_products = db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.is_active == True
    ).count()

    low_stock = db.query(Product).filter(
        Product.owner_id == current_user.id,
        Product.is_active == True,
        Product.quantity <= Product.low_stock_alert
    ).count()

    profit = total_sales - total_expenses

    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "profit": profit,
        "total_products": total_products,
        "low_stock_products": low_stock,
    }


@router.get("/daily")
def daily_report(
    date_str: str = Query(None, description="Tarehe: YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = date.today()

    sales = db.query(Sale).filter(
        Sale.owner_id == current_user.id,
        func.date(Sale.created_at) == target_date
    ).all()

    expenses = db.query(Expense).filter(
        Expense.owner_id == current_user.id,
        func.date(Expense.created_at) == target_date
    ).all()

    total_sales = sum(s.total_amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)

    return {
        "date": str(target_date),
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "profit": total_sales - total_expenses,
        "number_of_sales": len(sales),
        "number_of_expenses": len(expenses),
    }
