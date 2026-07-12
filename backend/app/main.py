from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import hcp, interactions, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First CRM - HCP Module API",
    description="Log Interaction Screen backend: FastAPI + LangGraph + Groq",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hcp.router)
app.include_router(interactions.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "hcp-crm-backend"}


@app.get("/health")
def health():
    return {"status": "healthy"}
