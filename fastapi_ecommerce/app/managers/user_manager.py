"""
User Manager

This file contains ALL business logic related to users.
The router calls these methods - it never touches the data directly.

Business rules specific to users:
- Email must be unique (no two users with same email)
- User ID is auto-generated
- When updating, email uniqueness is checked
"""

from typing import List, Optional
from app.data.store import users_db, next_user_id as global_next_id
from app.models.schemas import UserCreate, UserUpdate, User
from app.utils.loggers import logger

class UserManager:
    """
    Manager for user-related operations.
    
    All methods are @classmethod, meaning we don't need to create
    an instance. Just call UserManager.get_all_users() directly.
    """
    
    # Internal ID counter
    # The underscore (_) prefix means "private - don't access from outside"
    # We start from the value in store.py and increment as we create users
    _next_id: int = global_next_id

    @classmethod
    def get_all_users(
        cls,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get all users with optional pagination.
        
        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return
        
        Returns:
            List[User]: List of users
        """
        logger.info("Fetching all users")
        
        # Convert dictionary values to a list
        # users_db = {1: User(...), 2: User(...)}
        # .values() gives us: [User(...), User(...)]
        # list() converts it to a list we can slice
        users = list(users_db.values())
        
        # Apply pagination
        # [skip:skip+limit] means "start at position 'skip', go up to 'skip+limit'"
        result = users[skip:skip + limit]
        
        logger.debug(f"Returning {len(result)} users")
        return result
    
    @classmethod
    def get_user(cls, user_id: int) -> Optional[User]:
        """
        Get a single user by ID.
        
        Args:
            user_id: The unique identifier of the user
        
        Returns:
            User if found, None if user doesn't exist
        """
        logger.info(f"Looking up user ID: {user_id}")
        
        # .get() is SAFE - returns None if key doesn't exist
        # users_db[user_id] would CRASH if the key is missing
        # Always use .get() when you're not sure the key exists
        user = users_db.get(user_id)
        
        if user:
            logger.debug(f"Found user: {user.name}")
        else:
            logger.warning(f"User not found: ID {user_id}")
        
        return user
    
    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[User]:
        """
        Find a user by their email address.
        
        This is used to check for duplicate emails before creating
        or updating a user. Email must be unique in the system.
        
        Args:
            email: The email address to search for
        
        Returns:
            User if found, None if no user has this email
        """
        logger.debug(f"Searching for user with email: {email}")
        
        # Iterate through all users
        # users_db.values() gives us all User objects
        for user in users_db.values():
            # Case-insensitive comparison
            # "Ahmed@Example.com" and "ahmed@example.com" are the same
            if user.email.lower() == email.lower():
                logger.debug(f"Found user with email: {email}")
                return user
        
        logger.debug(f"No user found with email: {email}")
        return None
    
    @classmethod
    def create_user(cls, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Business rules:
        1. Email must be unique
        2. User ID is auto-generated
        
        Args:
            user_data: Validated user creation data
        
        Returns:
            User: The newly created user with assigned ID
        
        Raises:
            ValueError: If email already exists
            Exception: If user creation fails unexpectedly
        """
        logger.info(f"Creating new user: {user_data.name}")

        # BUSINESS RULE: Check for duplicate email
        existing_user = cls.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Cannot create user: email '{user_data.email}' already exists")
            raise ValueError(f"A user with email '{user_data.email}' already exists")
        
        try:
            new_id = cls._next_id
            cls._next_id += 1  # Increment the ID for the next user
            new_user = User(
                id=new_id,
                **user_data.model_dump()  # Convert Pydantic model to dict for unpacking
            )
            users_db[new_id] = new_user  # Save to "database"
            logger.info(f"User created with ID: {new_id}")
            return new_user
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise Exception(f"User Creation failed: {str(e)}")
        
    @classmethod
    def update_user(cls, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Business rules:
        1. User must exist
        2. Only provided fields are updated
        3. If email is updated, it must be unique
        
        Args:
            user_id: ID of the user to update
            user_data: New data (only provided fields)
        
        Returns:
            Updated User if found, None if user doesn't exist
        
        Raises:
            ValueError: If new email already belongs to another user
        """
        logger.info(f"Updating User ID: {user_id} with data: {update_data}")

        # Check if user exists
        existing_user = users_db.get(user_id)
        if not existing_user:
            logger.warning(f"User not Found for update: ID {user_id}")
            return None
        
        # Get only the fields the client actually sent
        # exclude_unset=True: if client didn't send "name", it won't be in update_dict
        update_dict = update_data.model_dump(eclude_unset=True)

        # BUSINESS RULE: If email is being updated, check it's unique
        if "email" in update_dict:
            # Check if another user already has this email
            existing_email_user = cls.get_user_by_email(update_dict["email"])

            # If someone else has this email, reject the update
            if existing_email_user and existing_email_user.id != user_id:
                logger.warning(f"Cannot update user: email '{update_dict['email']} already belongs to another user {existing_email_user.id}")
                raise ValueError(f"Email '{update_dict['email']}', is already in use")
        
        try:
            # Create updated user - keep old values where no update was provided
            updated_user = User(
                id=user_id,
                name=update_dict.get("name", existing_user.name),
                email=update_dict.get("email", existing_user.email),
            )
            
            # Save to database
            users_db[user_id] = updated_user
            
            logger.info(f"User updated successfully: ID {user_id}")
            return updated_user
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise Exception(f"User update failed: {str(e)}")

    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user_id: ID of the user to delete
        
        Returns:
            True if deleted, False if user not found
        """
        logger.info(f"Deleting User ID: {user_id}")

        if user_id in users_db:
            user_name = users_db[user_id].name
            del users_db[user_id]
            logger.info(f"User deleted Successfully: ID {user_id}, Name: {user_name}")
            return True
        logger.warning(f"User not found for deletion: ID {user_id}")
        return False
    




















