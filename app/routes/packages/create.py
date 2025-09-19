from app.routes.packages.packages import router
from app.core.routes import Routes # Your route configuration class
from app.schemas.packages import PackageOut
from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.schemas.packages import PackageBase as package_schema
from app import dependencies as deps
from app.schemas.packages import PackageBase as package_schema
from app.schemas import user as user_schema
from sqlalchemy.orm import Session
from app.crud.packages import create_package as create
from sqlite3 import IntegrityError

@router.post(Routes.Packages.default, response_model=PackageOut, status_code=status.HTTP_201_CREATED)
async def create_package_route(
    data: package_schema,
    current_user: user_schema.UserPublic = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    try:
        new_package = create(
            db=db,
            package=data,
            user_id=current_user.id,
        )
        return new_package

    except IntegrityError as e:
        db.rollback()
        # Common cases: duplicate name or repo_url
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Package with this name or repo_url already exists.",
        )

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the package.",
        )