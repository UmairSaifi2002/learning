"""
User Router

Handles HTTP requests for user endpoints.
Pattern is IDENTICAL to products router.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.managers.user_manager import UserManager
from app.models.schemas import UserCreate, UserUpdate, User, MessageResponse
from app.utils.loggers import logger

# Create router with prefix and tag
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """
    Get all users with pagination.
    
    Args:
        skip: Skip first N users (default 0)
        limit: Maximum users to return (default 100)
    """
    logger.info(f"GET /users - skip={skip}, limit={limit}")
    
    try:
        users = UserManager.get_all_users(skip=skip, limit=limit)
        logger.info(f"Returning {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Get a single user by ID.
    
    Args:
        user_id: User's unique ID (path parameter)
    """
    logger.info(f"GET /users/{user_id}")
    
    user = UserManager.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user.
    
    Args:
        user: User data (request body)
            - name: Full name (required)
            - email: Email address (required, must be unique)
    """
    logger.info(f"POST /users - Creating: {user.name}")
    
    try:
        new_user = UserManager.create_user(user)
        return new_user
    except ValueError as e:
        # ValueError means business rule violation (duplicate email)
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """
    Update an existing user.
    
    Args:
        user_id: User's unique ID (path parameter)
        user: Updated user data (request body, all fields optional)
    """
    logger.info(f"PUT /users/{user_id}")
    
    try:
        updated_user = UserManager.update_user(user_id, user)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return updated_user
        
    except ValueError as e:
        # Duplicate email during update
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int):
    """
    Delete a user.
    
    Args:
        user_id: User's unique ID (path parameter)
    """
    logger.info(f"DELETE /users/{user_id}")
    
    deleted = UserManager.delete_user(user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return MessageResponse(
        message=f"User {user_id} deleted successfully"
    )










