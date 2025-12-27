from fastapi import FastAPI
from datetime import datetime

from app.database import Base, engine
from app.routes import router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Webhook Processor")

@app.get("/")
def health_check():
    return {
        "status": "HEALTHY",
        "current_time": datetime.utcnow().isoformat()
    }

app.include_router(router)
