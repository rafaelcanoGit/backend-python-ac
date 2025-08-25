from pydantic import BaseModel
from typing import Optional, List, Any


class ChatState(BaseModel):
    """Estado de conversación para LangGraph"""

    prompt_template: Any = None
    user_phone: Optional[str] = None
    user_message: Optional[str] = None
    memories: List[str] = []
    response: Optional[Any] = None        # Raw LLM response
    responses: List[dict] = []            # Processed responses
    error: Optional[str] = None           # Error message if any
    other_input: Optional[Any] = None
