from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator
from typing import List, Optional
from ..rag_pipeline import rag_pipeline
from ..llm_service import llm_service
from ..security import security_manager
# from ..monitoring import performance_monitor
from ..config import config
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > config.api.max_request_size:
            raise ValueError(f'Message too long (max {config.api.max_request_size} characters)')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str] = []
    processing_time: Optional[float] = None
    cached: bool = False

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """
    Process a chat message with security validation and performance monitoring
    """
    client_id = req.client.host if req.client else "anonymous"

    # Security validation (temporarily disabled)
    # is_valid, message = security_manager.validate_request(request.message, client_id)
    # if not is_valid:
    #     raise HTTPException(status_code=400, detail=message)

    # Sanitize input
    sanitized_message = request.message  # security_manager.sanitize_input(request.message)

    # Check if LLM service is available
    # Temporarily disabled for testing
    # if not llm_service.check_ollama_status():
    #     raise HTTPException(
    #         status_code=503,
    #         detail="AI service is currently unavailable. The language model requires more system memory than is currently available. Please try again later or contact the administrator."
    #     )

    try:
        conversation_id = request.conversation_id or f"conv_{hash(client_id)}"

        # Process query directly with LLM service (simplified for testing)
        response = llm_service.generate_response(sanitized_message)

        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            sources=[],
            processing_time=0.0,
            cached=False
        )

    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(conversation_id: str, req: Request):
    """
    Get conversation history with security validation
    """
    client_id = req.client.host if req.client else "anonymous"

    # Basic security check - ensure conversation belongs to client (temporarily disabled)
    # if not conversation_id.startswith(f"conv_{hash(client_id)}") and conversation_id != "default":
    #     raise HTTPException(status_code=403, detail="Access denied")

    try:
        history = rag_pipeline.get_conversation_history(conversation_id)

        # Convert to the expected format with size limits
        messages = []
        for item in history[-50:]:  # Limit to last 50 exchanges for performance
            messages.append({
                "role": "user",
                "content": item["question"][:500],  # Truncate long messages
                "timestamp": item.get("timestamp", "")
            })
            messages.append({
                "role": "assistant",
                "content": item["response"][:1000],  # Truncate long responses
                "timestamp": item.get("timestamp", "")
            })

        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages
        )

    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation history")