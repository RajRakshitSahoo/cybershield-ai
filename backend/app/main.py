from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, analyze, history, compare, report, dashboard, admin, domain, security, ml

app = FastAPI(
    title=settings.app_name,
    description="AI-powered phishing website detection & domain intelligence platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(compare.router)
app.include_router(report.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(domain.router)
app.include_router(security.router)
app.include_router(ml.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
