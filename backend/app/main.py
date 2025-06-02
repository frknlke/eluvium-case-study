from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import mailbox
from .routers import search

app = FastAPI(
    title="Eluvium Backend API",
    description="Backend API for the Eluvium Gmail OAuth application",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:8000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mailbox.router)
app.include_router(search.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Eluvium Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"} 