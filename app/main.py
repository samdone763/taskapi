from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db.session import Base, engine

# Import models zote ili ziundwe kwenye database
from app.models import user, task, product, sale, employee, expense

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BizManager API",
    description="REST API ya Kusimamia Biashara Ndogo - Afrika",
    version="2.0.0",
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "2.0.0"}
