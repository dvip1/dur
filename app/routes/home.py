from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database.models.user import User
from app.routes.auth import get_current_user
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse, )
async def Home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
