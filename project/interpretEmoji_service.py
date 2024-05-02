import prisma
import prisma.models
from pydantic import BaseModel


class EmojiInterpretationResponse(BaseModel):
    """
    This model outlines the expected response from the API, which is a simple string explaining the significance of the emoji.
    """

    interpretation: str


async def interpretEmoji(emoji: str) -> EmojiInterpretationResponse:
    """
    This function interprets the meaning of a given emoji by querying a database for an associated explanation.

    Args:
        emoji (str): The emoji character that needs to be interpreted.

    Returns:
        EmojiInterpretationResponse: A model containing the textual interpretation of the emoji.

    Example:
        emoji = '😊'
        result = await interpretEmoji(emoji)
        print(result.interpretation)
        > "A smiley face that indicates happiness."
    """
    interpretation_record = await prisma.models.Interpretation.prisma().find_unique(
        where={"emoji": emoji}
    )
    if interpretation_record:
        return EmojiInterpretationResponse(
            interpretation=interpretation_record.explanation
        )
    else:
        return EmojiInterpretationResponse(
            interpretation="No interpretation available."
        )
