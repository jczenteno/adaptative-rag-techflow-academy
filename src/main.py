import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()
from src.routes.chatbot_router import router as chatbot_router
from src.llm.llm_factory import LLMFactory
from src.agent.agent import ChatbotGraph
from langgraph.checkpoint.postgres import PostgresSaver
from src.service.chatbot_service import ChatbotService
from src.db.postgres import init_pool, close_pool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_chatbot_graph():
    try:
        logger.info("Inicializando grafo LangGraph para el chatbot...")
        
        # Creacion de la instancia de modelo LLM
        model_provider = os.getenv('MODEL_PROVIDER', 'openai')
        chat_model = LLMFactory().create_chat_model(model_provider)
        
        # Instanciar checkpointer Postgres
        postgres_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
        if not postgres_url:
            raise ValueError("POSTGRES_URL o DATABASE_URL no está configurado en .env")

        # Inicializar pool de Postgres reutilizable para tools (misma instancia/DSN)
        init_pool(postgres_url)

        # Crear checkpointer desde cadena de conexión (context manager)
        # Guardamos el gestor en app.state para cerrar al apagar si se requiere
        saver_cm = PostgresSaver.from_conn_string(postgres_url)
        app.state.checkpointer_cm = saver_cm
        checkpointer = saver_cm.__enter__()
        # Crear tablas la primera vez
        checkpointer.setup()

        # Inicializacion del grafo con el modelo y el checkpointer
        chatbot_graph = ChatbotGraph(chat_model, checkpointer)
        
        # Configuracion del servicio con el grafo inicializado
        ChatbotService.set_chatbot_graph(chatbot_graph)
        
        logger.info("Grafo LangGraph inicializado correctamente")
        return chatbot_graph
    except Exception as e:
        logger.error(f"Error al inicializar el grafo LangGraph: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_chatbot_graph()
    try:
        yield
    finally:
        # Cerrar el pool de Postgres
        try:
            close_pool()
        except Exception as e:
            logger.error(f"Error al cerrar pool Postgres: {e}")

        # Cerrar el context manager del checkpointer si existe
        saver_cm = getattr(app.state, "checkpointer_cm", None)
        if saver_cm is not None:
            try:
                saver_cm.__exit__(None, None, None)
            except Exception as e:
                logger.error(f"Error al cerrar checkpointer: {e}")


app = FastAPI(
    title="Chatbot API",
    description="API for processing chatbot questions",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=True)
