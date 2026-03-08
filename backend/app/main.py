
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as api_router
from backend.app.database import create_db_and_tables, close_db_connection



app = FastAPI(title="Claude Analytics API",
    description="Analytics platform for Claude Code telemetry",
    version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection and tables
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection()

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Claude Code Analytics Platform!"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
