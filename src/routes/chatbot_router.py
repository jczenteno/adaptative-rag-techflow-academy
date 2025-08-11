from fastapi import APIRouter
from src.controller.chatbot_controller import ChatbotController
from src.entities.chatbot_entities import ChatbotRequest

router = APIRouter(prefix="/api", tags=["chatbot"])

# Crear una instancia del controlador
chatbot_controller = ChatbotController()

@router.post("/chatbot", summary="Process chatbot question")
async def chatbot_endpoint(request: ChatbotRequest):
    return await chatbot_controller.process_chatbot_request(request)

@router.get("/chatbot/history", summary="Get chat history")
async def chatbot_history_endpoint(user: str):
    return await chatbot_controller.get_chat_history(user)
