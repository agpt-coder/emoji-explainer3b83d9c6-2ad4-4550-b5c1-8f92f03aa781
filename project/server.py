import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Optional

import project.deleteUser_service
import project.explainEmoji_service
import project.getUserDetails_service
import project.handleError_service
import project.interpretEmoji_service
import project.loginUser_service
import project.registerUser_service
import project.updateUser_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="emoji-explainer",
    lifespan=lifespan,
    description="create a single endpoint that takes in an emoji and explains what it means. Use groq and llama3 for the explaination",
)


@app.patch(
    "/users/update", response_model=project.updateUser_service.UpdateUserProfileResponse
)
async def api_patch_updateUser(
    username: str, email: str
) -> project.updateUser_service.UpdateUserProfileResponse | Response:
    """
    This endpoint allows the user to update their profile information like username or email. It requires JWT token authentication and changes are saved to the user database.
    """
    try:
        res = await project.updateUser_service.updateUser(username, email)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/api/error", response_model=project.handleError_service.ErrorResponse)
async def api_post_handleError(
    module: str,
    timestamp: datetime,
    error_message: str,
    user_role: project.handleError_service.Role,
    additional_info: Optional[Dict[str, str]],
) -> project.handleError_service.ErrorResponse | Response:
    """
    This route is used for handling errors that occur within the application. When an interaction with the Emoji Interpretation Module results in an error, this endpoint captures the error details and logs them for debugging purposes. It provides a user-friendly error message to the client, suggesting potential corrective actions or informing them about the issue. The API accepts JSON format containing specific details about the error context to better assist in tracing and resolving the issue.
    """
    try:
        res = await project.handleError_service.handleError(
            module, timestamp, error_message, user_role, additional_info
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/emoji/interpret",
    response_model=project.interpretEmoji_service.EmojiInterpretationResponse,
)
async def api_post_interpretEmoji(
    emoji: str,
) -> project.interpretEmoji_service.EmojiInterpretationResponse | Response:
    """
    This endpoint accepts a POST request containing an emoji character in the request body. It uses GROQ to query the underlying data and llama3 to process the natural language understanding needed to interpret the emoji. The User Management Module verifies the user's authentication. In case of any errors during the process, the Error Handling Module intercepts and provides appropriate feedback. The response will be a string describing the emoji's meaning.
    """
    try:
        res = await project.interpretEmoji_service.interpretEmoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users/login", response_model=project.loginUser_service.LoginResponse)
async def api_post_loginUser(
    email: str, password: str
) -> project.loginUser_service.LoginResponse | Response:
    """
    This endpoint authenticates a user by their email and password. On successful authentication, it returns a JWT token which is used to authenticate subsequent requests. The JWT token includes a payload with the user's role and ID.
    """
    try:
        res = await project.loginUser_service.loginUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/details", response_model=project.getUserDetails_service.UserDetailsResponse
)
async def api_get_getUserDetails(
    request: project.getUserDetails_service.UserDetailsRequest,
) -> project.getUserDetails_service.UserDetailsResponse | Response:
    """
    This protected route fetches detailed information of the authenticated user, such as username, and role. It requires JWT token authentication. The information is fetched from the user database using user ID from the JWT token payload.
    """
    try:
        res = await project.getUserDetails_service.getUserDetails(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/explain", response_model=project.explainEmoji_service.EmojiExplainResponse
)
async def api_post_explainEmoji(
    emoji: str,
) -> project.explainEmoji_service.EmojiExplainResponse | Response:
    """
    This endpoint receives an emoji as input via POST request in JSON format. It queries the Emoji Interpretation Module using GROQ to retrieve the meaning of the emoji and leverages llama3 for advanced interpretation. The response is a detailed explanation of the emoji in text format. This endpoint primarily handles JSON content types and expects a key-value pair in the request body with 'emoji' as the key and the emoji character as the value.
    """
    try:
        res = await project.explainEmoji_service.explainEmoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/users/delete", response_model=project.deleteUser_service.DeleteUserResponse
)
async def api_delete_deleteUser(
    Authorization: str,
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    Enables a user to delete their account. It requires JWT token authentication. Once authenticated, it removes the user's data from the database.
    """
    try:
        res = await project.deleteUser_service.deleteUser(Authorization)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/users/register",
    response_model=project.registerUser_service.UserRegistrationResponse,
)
async def api_post_registerUser(
    username: str, email: str, password: str
) -> project.registerUser_service.UserRegistrationResponse | Response:
    """
    This endpoint allows new users to register. It expects a JSON with username, email, and password. On successful registration, it returns a user object and status code 201. It uses standard Bcrypt for password hashing to ensure security.
    """
    try:
        res = await project.registerUser_service.registerUser(username, email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
