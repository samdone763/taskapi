from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.db.session import Base, engine
from app.models import user, task, product, sale, employee, expense

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BizManager API",
    description="REST API ya Kusimamia Biashara Ndogo - Afrika",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "2.0.0"}
