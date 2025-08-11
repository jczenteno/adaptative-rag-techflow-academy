from fastapi import HTTPException
from typing import Dict, Any
from src.service.chatbot_service import ChatbotService
from src.entities.chatbot_entities import ChatbotRequest

class ChatbotController:
    @staticmethod
    async def process_chatbot_request(request: ChatbotRequest) -> Dict[str, Any]:
        try:
            return await ChatbotService.process_question(
                question=request.question,
                user=request.user
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

    @staticmethod
    async def get_chat_history(user: str) -> Dict[str, Any]:
        return await ChatbotService.get_chat_history(user)