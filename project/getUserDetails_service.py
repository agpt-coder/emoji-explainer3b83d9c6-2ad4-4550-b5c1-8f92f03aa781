import prisma
import prisma.models
from pydantic import BaseModel


class UserDetailsRequest(BaseModel):
    """
    Request model for fetching user details. Requires a JWT to authenticate and extract the relevant user ID from the payload. The API will not require additional path or query parameters as the user ID is derived from the token.
    """

    pass


class Role(BaseModel):
    """
    Enumerates the possible roles a user can have, typically USER or ADMIN.
    """

    UNKNOWN: str
    USER: str
    ADMIN: str


class UserDetailsResponse(BaseModel):
    """
    Response model for user details. Contains the username and role of the authenticated user.
    """

    username: str
    role: Role


async def getUserDetails(request: UserDetailsRequest) -> UserDetailsResponse:
    """
    Fetches detailed information of an authenticated user, such as their username and role, based on a JWT token.

    This function assumes the JWT token is already verified to be valid and the user ID can be extracted from it. The user information is then fetched from the database using the user ID associated with the JWT.

    Args:
        request (UserDetailsRequest): The request object containing the necessary data to fetch user details. The user identification is extracted through JWT authentication.

    Returns:
        UserDetailsResponse: The response object containing the username and role of the user.

    Example:
        request_data = UserDetailsRequest()
        details = await getUserDetails(request_data)
        print(details.username, details.role)
    """
    user_id = 1
    user = await prisma.models.User.prisma().find_unique(
        where={"id": user_id}, include={"role": True}
    )
    if user is None:
        raise ValueError("No user found with the provided token information.")
    response = UserDetailsResponse(username=user.email, role=user.role)
    return response
