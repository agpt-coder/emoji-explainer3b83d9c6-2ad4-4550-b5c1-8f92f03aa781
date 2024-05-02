import prisma
import prisma.models
from pydantic import BaseModel


class UpdateUserProfileResponse(BaseModel):
    """
    This model returns the status of the update operation, indicating whether it was successful or not.
    """

    success: bool
    message: str


async def updateUser(username: str, email: str) -> UpdateUserProfileResponse:
    """
    This endpoint allows the user to update their profile information like username or email. It requires JWT token authentication and changes are saved to the user database.

    Args:
    username (str): New username that the user wishes to update to.
    email (str): New email address for the user account.

    Returns:
    UpdateUserProfileResponse: This model returns the status of the update operation, indicating whether it was successful or not.
    """
    try:
        existing_user = await prisma.models.User.prisma().find_unique(
            where={"email": email}
        )
        if existing_user:
            return UpdateUserProfileResponse(
                success=False, message="Email is already in use by another account."
            )
        user = await prisma.models.User.prisma().find_unique(where={"email": username})
        if not user:
            return UpdateUserProfileResponse(success=False, message="User not found.")
        updated_user = await prisma.models.User.prisma().update(
            where={"id": user.id}, data={"email": email}
        )
        return UpdateUserProfileResponse(
            success=True, message="User profile updated successfully."
        )
    except Exception as e:
        return UpdateUserProfileResponse(
            success=False, message=f"An error occurred: {str(e)}"
        )
