from fastapi import APIRouter
from app.api.v1.endpoints import auth, tasks, products, sales, employees, expenses, reports

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(products.router)
api_router.include_router(sales.router)
api_router.include_router(employees.router)
api_router.include_router(expenses.router)
api_router.include_router(reports.router)
