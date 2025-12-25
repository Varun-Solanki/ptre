# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from src.api.routes import router

# app = FastAPI(title="PTRE Signal Engine")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # React dev server
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes import router

# -----------------------------
# Create FastAPI app (CRITICAL)
# -----------------------------
app = FastAPI(
    title="PTRE Signal Engine",
    version="1.0",
    description="Trend + Momentum based market intelligence"
)

# -----------------------------
# CORS Configuration
# -----------------------------
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# API Routes
# -----------------------------
app.include_router(router)


