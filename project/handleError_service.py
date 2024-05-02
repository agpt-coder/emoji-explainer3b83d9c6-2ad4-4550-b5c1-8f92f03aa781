from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Role(BaseModel):
    """
    Enumerates the possible roles a user can have, typically USER or ADMIN.
    """

    UNKNOWN: str
    USER: str
    ADMIN: str


class ErrorResponse(BaseModel):
    """
    This model provides a user-friendly error message and potential corrective actions to the client.
    """

    user_message: str
    suggested_actions: Optional[List[str]] = None
    reference_code: str


class LogLevel(Enum):
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"


async def handleError(
    module: str,
    timestamp: datetime,
    error_message: str,
    user_role: Role,
    additional_info: Optional[Dict[str, str]],
) -> ErrorResponse:
    """
    This function is responsible for handling errors raised by various modules, logging them with appropriate information
    and providing a structured error message to the user.

    Args:
        module (str): Name of the module where error occurred. Useful for categorizing the error.
        timestamp (datetime): Timestamp of when the error was logged.
        error_message (str): Detailed error message.
        user_role (Role): Role of the user involved in the error situation.
        additional_info (Optional[Dict[str, str]]): Additional contextual data about the error that can assist in debugging.

    Returns:
        ErrorResponse: Values containing user-friendly error message and actions to remedy the situation, if applicable.

    Example:
        module = "ProcessingModule"
        timestamp = datetime.utcnow()
        error_message = "Failed to process the data due to invalid input format."
        user_role = Role.USER
        additional_info = {"input_value": "text"}

        response = {
            "user_message": "A processing error occurred. Please check the input format.",
            "suggested_actions": ["Check the data format before submitting.", "Contact support if the error persists."],
            "reference_code": "ERR67890"
        }

        e_response = handleError(module, timestamp, error_message, user_role, additional_info)

        print(e_response)
    """
    await prisma.models.Log.prisma().create(
        data={
            "message": f"Error in {module}: {error_message}. Additional Info: {additional_info}",
            "level": LogLevel.ERROR,
            "createdAt": timestamp,
        }
    )
    error_response = ErrorResponse(
        user_message="There was an internal error, please try again later.",
        suggested_actions=[
            "Please check the information provided and try again.",
            "If the problem persists, contact customer support.",
        ],
        reference_code="ERR" + str(int(timestamp.timestamp())),
    )
    return error_response
