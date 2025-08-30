from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import STATIC_DIR, TEMPLATES_DIR
from app.routes import auth
from app.routes import home
app = FastAPI()

app.include_router(auth.router)
app.include_router(home.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
