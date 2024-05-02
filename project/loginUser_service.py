import bcrypt
import jwt
import prisma
import prisma.models
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    Response model post successful authentication. It contains the JWT token used for subsequent requests.
    """

    jwt_token: str


async def loginUser(email: str, password: str) -> LoginResponse:
    """
    This endpoint authenticates a user by their email and password. On successful authentication, it returns a JWT token which is used to authenticate subsequent requests. The JWT token includes a payload with the user's role and ID.

    Args:
        email (str): The email associated with the user's account.
        password (str): The password associated with the user's account. This should be sent securely and handled with care.

    Returns:
        LoginResponse: Response model post successful authentication. It contains the JWT token used for subsequent requests.

    Example:
        loginUser('example@example.com', 'securepassword123')
        # Returns instance of LoginResponse with a valid jwt_token if credentials are correct, otherwise raises an Exception.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if user and bcrypt.checkpw(
        password.encode("utf-8"), user.hashedPassword.encode("utf-8")
    ):
        payload = {"user_id": user.id, "role": user.role.name}
        secret = "YOUR_SECRET_KEY"
        token = jwt.encode(payload, secret, algorithm="HS256")
        return LoginResponse(jwt_token=token)
    else:
        raise Exception("Invalid login credentials")
