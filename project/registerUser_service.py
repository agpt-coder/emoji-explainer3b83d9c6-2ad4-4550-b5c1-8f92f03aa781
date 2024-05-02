import bcrypt
import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class Role(BaseModel):
    """
    Enumerates the possible roles a user can have, typically USER or ADMIN.
    """

    UNKNOWN: str
    USER: str
    ADMIN: str


class UserRegistrationResponse(BaseModel):
    """
    This model defines the structure of the response after a successful user registration. It returns the registered user's details except the password.
    """

    id: int
    username: str
    email: str
    role: Role


async def registerUser(
    username: str, email: str, password: str
) -> UserRegistrationResponse:
    """
    This endpoint allows new users to register. It expects a username, email, and password.
    On successful registration, it returns a user object and status code 201.
    It uses standard Bcrypt for password hashing to ensure security.

    Args:
        username (str): The desired username for the new user. Must be unique across users.
        email (str): Email address for the user, used for authentication purposes. Must be unique.
        password (str): Password for the account, which will be hashed using Bcrypt before storage.

    Returns:
        UserRegistrationResponse: This model defines the structure of the response after a successful user registration,
                                  It returns the registered user's details except the password.
    """
    existing_user = await prisma.models.User.prisma().find_first(
        where={"OR": [{"email": email}, {"username": username}]}
    )
    if existing_user:
        raise ValueError("A user with the same email or username already exists.")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    user = await prisma.models.User.prisma().create(
        data={
            "username": username,
            "email": email,
            "hashedPassword": hashed_password,
            "role": prisma.enums.Role.USER,
        }
    )
    return UserRegistrationResponse(
        id=user.id, username=user.username, email=user.email, role=Role.USER
    )  # TODO(autogpt): Cannot access attribute "username" for class "User"


#     Attribute "username" is unknown. reportAttributeAccessIssue
