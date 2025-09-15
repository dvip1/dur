from fastapi import APIRouter, Request
from app.database.models.packages import Package
from app.database.models.user import User
from app.routes.auth import get_current_user
router = APIRouter()

@router.get("/packages")
async def list_packages(request: Request, current_user: User = get_current_user):
    packages = request.state.db.query(Package).all()
    return {"packages": [pkg.name for pkg in packages]}

@router.post("/packages")
async def create_package(request: Request, name: str, repo_url: str, description: str, current_user: User = get_current_user):
    new_package = Package(name=name,description= description, repo_url=repo_url, created_by=current_user.id)
    request.state.db.add(new_package)
    request.state.db.commit()
    return {"message": f"Package '{name}' created successfully."}
