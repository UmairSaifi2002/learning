"""
User Manager - MySQL Database Version
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import User
from app.models.schemas import UserCreate, UserUpdate
from app.utils.loggers import logger


class UserManager:

    @staticmethod
    async def get_all_users(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        logger.info("Fetching all users")
        query = select(User).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_user(
        session: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        logger.info(f"Looking up user ID: {user_id}")
        return await session.get(User, user_id)

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Find user by email (case-insensitive)."""
        logger.debug(f"Searching for user with email: {email}")
        query = select(User).where(User.email.ilike(email))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        user_data: UserCreate
    ) -> User:
        logger.info(f"Creating new user: {user_data.name}")
        
        # Check for duplicate email
        existing = await UserManager.get_user_by_email(session, user_data.email)
        if existing:
            raise ValueError(f"A user with email '{user_data.email}' already exists")
        
        try:
            new_user = User(**user_data.model_dump())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info(f"User created: ID {new_user.id}")
            return new_user
        except ValueError:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise Exception(f"User creation failed: {str(e)}")

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        logger.info(f"Updating user ID: {user_id}")
        
        user = await session.get(User, user_id)
        if not user:
            return None
        
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # Check email uniqueness if being updated
        if "email" in update_dict:
            existing = await UserManager.get_user_by_email(session, update_dict["email"])
            if existing and existing.id != user_id:
                raise ValueError(f"Email '{update_dict['email']}' is already in use")
        
        try:
            if "name" in update_dict:
                user.name = update_dict["name"]
            if "email" in update_dict:
                user.email = update_dict["email"]
            
            await session.commit()
            await session.refresh(user)
            return user
        except ValueError:
            raise
        except Exception as e:
            await session.rollback()
            raise Exception(f"User update failed: {str(e)}")

    @staticmethod
    async def delete_user(
        session: AsyncSession,
        user_id: int
    ) -> bool:
        logger.info(f"Deleting user ID: {user_id}")
        
        user = await session.get(User, user_id)
        if not user:
            return False
        
        try:
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise Exception(f"User deletion failed: {str(e)}")