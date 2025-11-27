from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import STATIC_DIR, TEMPLATES_DIR
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import base
from app.routes.packages import packages
app = FastAPI()

app.include_router(base.router)
app.include_router(packages.router)
origins = [
    "http://localhost:3000",  # Your Next.js development server URL
    # "https://your-nextjs-app.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of origins allowed to make requests
    allow_credentials=True,       # Allow cookies to be included in requests
    allow_methods=["*"],          # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
