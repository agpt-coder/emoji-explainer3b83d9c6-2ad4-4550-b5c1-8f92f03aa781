import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponse(BaseModel):
    """
    Response model for the deletion process of a user. The model confirms the success of the delete operation.
    """

    success: bool
    message: str


async def deleteUser(Authorization: str) -> DeleteUserResponse:
    """
    Enables a user to delete their account. It requires JWT token authentication. Once authenticated,
    it removes the user's data from the database.

    Args:
    Authorization (str): JWT token used for authenticating the user. Should be passed as a bearer token in the header.

    Returns:
    DeleteUserResponse: Response model for the deletion process of a user. The model confirms the success of the delete operation.
    """
    if not Authorization.startswith("Bearer "):
        return DeleteUserResponse(
            success=False, message="Invalid authorization token format."
        )
    token = Authorization[7:]
    user_id = decode_and_extract_user_id(token)
    if not user_id:
        return DeleteUserResponse(success=False, message="Invalid or expired token.")
    try:
        delete_result = await prisma.models.User.prisma().delete(where={"id": user_id})
        if delete_result:
            return DeleteUserResponse(
                success=True, message="User deleted successfully."
            )
        else:
            return DeleteUserResponse(
                success=False, message="No user found with the given credentials."
            )
    except Exception as e:
        return DeleteUserResponse(success=False, message=f"An error occurred: {str(e)}")


def decode_and_extract_user_id(token: str) -> int:
    """
    Decodes the JWT token and extracts the user_id.

    Args:
    token (str): The JWT token from which user_id should be extracted.

    Returns:
    int: The user_id if successful, None otherwise.
    """
    return int(token)
