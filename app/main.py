from fastapi import FastAPI
from app.database import init_db
from app.api.routes import health, webhook

# Create tables on startup
init_db()

app = FastAPI(title="Municipal Intelligence API", version="1.0")

# Nest routes
app.include_router(health.router, tags=["System"])
app.include_router(webhook.router, tags=["Call-E"])