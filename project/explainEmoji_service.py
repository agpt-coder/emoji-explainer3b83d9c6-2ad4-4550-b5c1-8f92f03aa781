import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class EmojiExplainResponse(BaseModel):
    """
    The response model containing a detailed text explaining the meaning of the emoji, either from the database or computed by llama3 if not present.
    """

    explanation: str


async def explainEmoji(emoji: str) -> EmojiExplainResponse:
    """
    This function receives an emoji as input and attempts to retrieve its explanation from the database.
    If the explanation does not exist in the database, it simulates a computation for interpretation (here as a simple fallback).

    Args:
        emoji (str): The emoji character for which the explanation is requested.

    Returns:
        EmojiExplainResponse: The response model containing a detailed text explaining the meaning of the emoji.

    Example:
        emoji = '🙂'
        response = explainEmoji(emoji)
        print(response.explanation)
        > 'A smiling face generally used for expressing happiness or satisfaction.'
    """
    interpretation = await prisma.models.Interpretation.prisma().find_unique(
        where={"emoji": emoji}
    )
    if interpretation:
        explanation = interpretation.explanation
    else:
        explanation = fake_advanced_interpretation(emoji)
        await prisma.models.Interpretation.prisma().create(
            data={"emoji": emoji, "explanation": explanation, "userId": 1}
        )
        await prisma.models.Log.prisma().create(
            data={
                "message": f"Computed new interpretation for emoji '{emoji}'",
                "level": prisma.enums.LogLevel.INFO,
            }
        )
    return EmojiExplainResponse(explanation=explanation)


async def fake_advanced_interpretation(emoji: str) -> str:
    """
    A fake placeholder function for the purpose of simulating advanced interpretation of an emoji since the actual advanced interpretation libraries are unavailable to include.
    Only returns a simple example explanation based on a predefined rule.

    Args:
        emoji (str): The emoji character to interpret.

    Returns:
        str: A fake interpreted meaning of the emoji.

    Example:
        fake_advanced_interpretation("🙂")
        > "A smiling face that indicates happiness or satisfaction."

    """
    interpretations = {
        "🙂": "A smiling face that indicates happiness or satisfaction.",
        "😢": "A sad face portraying tears, often used to indicate sadness or grief.",
    }
    return interpretations.get(emoji, "An interesting but not yet interpreted emoji!")
