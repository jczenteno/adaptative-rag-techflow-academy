from typing import Dict, Any
import os
import datetime
from src.llm.llm_factory import LLMFactory
from src.agent.agent import ChatbotGraph

class ChatbotService:
    _chatbot_graph = None
    
    @classmethod
    def set_chatbot_graph(cls, graph: ChatbotGraph):
        cls._chatbot_graph = graph
    
    @classmethod
    async def process_question(cls, question: str, user: str) -> Dict[str, Any]:
        result = cls._chatbot_graph.process_message(question, user)
        
        # Agregar timestamp a la respuesta
        current_time = datetime.datetime.now().isoformat()
        result["processed_timestamp"] = current_time
        
        return result
    
    @classmethod
    async def get_chat_history(cls, user: str) -> Dict[str, Any]:
        history = cls._chatbot_graph.get_chat_history(user)
        
        return {
            "user": user,
            "messages": history
        }