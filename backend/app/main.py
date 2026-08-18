from fastapi import FastAPI
from backend.app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.get('/health',tags=['health'])
def health_check():
    return {
        "status" : "online",
        "project" : settings.PROJECT_NAME,
        "version" : "1.0.0"
    }

