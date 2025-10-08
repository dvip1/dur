# list_packages.py

from typing import List
from app.routes.packages.packages import router
from app import dependencies as deps
from app.core.routes_version1 import Routes # Your route configuration class
from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.schemas import user as user_schema
from app.schemas.packages import PackageOut # Import the output schema
from sqlalchemy.orm import Session
from app.database.models.packages import Package

@router.get(
    Routes.Packages.default,
    response_model=List[PackageOut], # Defines the successful response structure
    summary="List all packages",
    response_description="A list of all registered packages.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "An unexpected error occurred on the server.",
            "content": {
                "application/json": {
                    "example": {"detail": "Error retrieving packages from the database."}
                }
            },
        },
    },
)
async def list_packages(
    request: Request,
    current_user: user_schema.UserPublic = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    ### List all available packages 📦

    Retrieves a complete list of all packages registered in the system.

    - This endpoint requires the user to be **authenticated**.
    - Returns an array of package objects, each including details like name, description, and repository URL.
    """
    try:
        # Fetch all package objects from the database
        packages = db.query(Package).all()
        # FastAPI will automatically serialize this list of ORM objects
        # into a list of PackageOut schemas for the response.
        return packages
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching packages: {e}")
        # Raise a standard 500 error to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving packages.",
        )