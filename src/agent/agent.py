import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from typing_extensions import TypedDict, Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from typing import Any as _Any
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from src.agent.tools import (
    registrar_cliente,
    contar_registros,
    get_current_date,
    get_program_price,
)
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.prompts import MODEL_SYSTEM_MESSAGE, COMPLEXITY_PROMPT, TOOL_ROUTER_PROMPT, SIMPLE_PROMPT, RAG_PROMPT, TOOL_PROMPT
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.runnables import RunnablePassthrough
from src.llm.llm_factory import LLMFactory, LLMProvider
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models para structured output
class ComplexityLevel(BaseModel):
    """Modelo para clasificación de complejidad"""
    complexity_level: str

class ToolSelection(BaseModel):
    """Modelo para selección de herramientas"""
    tool_name: str

# Estado personalizado que extiende MessagesState
class AdaptiveAgentState(TypedDict):
    """
    Estado personalizado que incluye mensajes y metadatos del RAG adaptativo
    """
    messages: Annotated[List[BaseMessage], add_messages]
    complexity_level: Optional[str]
    retrieved_docs: Optional[List[Any]]

class ChatbotGraph:
    def __init__(self, chat_model: BaseChatModel, checkpointer: _Any):
        self.model = chat_model.bind_tools([
            registrar_cliente,
            contar_registros,
            get_current_date,
            get_program_price,
        ])
        
        # Setup LLM para clasificadores
        self.setup_llm()
        
        # Setup Qdrant vector store
        self.setup_qdrant()
        
        # Setup clasificadores
        self.setup_classifiers()
        
        # Checkpointer (inyectado desde el ciclo de vida de la app)
        if checkpointer is None:
            raise ValueError("Se requiere un checkpointer para inicializar ChatbotGraph")
        self.within_thread_memory = checkpointer
        
        # Construir y compilar el grafo
        self.graph = self._build_graph()
        
        # Diccionario para almacenar los thread_ids por usuario
        self.user_threads = {}

        # Límite de mensajes de historial a enviar al LLM (configurable por env)
        # Variable: MESSAGE_HISTORY_LIMIT (por defecto 10)
        try:
            self.message_history_limit = int(os.getenv("MESSAGE_HISTORY_LIMIT", "10"))
        except Exception:
            self.message_history_limit = 10
    
    def _get_last_messages(self, state: "AdaptiveAgentState", limit: Optional[int] = None) -> List[BaseMessage]:
        effective_limit = limit if isinstance(limit, int) and limit > 0 else self.message_history_limit
        messages = state.get("messages", [])
        if not messages:
            return []
        if len(messages) <= effective_limit:
            return messages
        return messages[-effective_limit:]

    def setup_llm(self):
        """Configure LLM para clasificadores"""
        llm_factory = LLMFactory()
        self.llm = llm_factory.create_chat_model(LLMProvider.OPENAI, temperature=0)
        self.llm_json = llm_factory.create_chat_model(LLMProvider.OPENAI, temperature=0)
    
    def setup_qdrant(self):
        """Setup Qdrant vector store"""
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_key = os.getenv('QDRANT_KEY')
        collection_name = os.getenv('QDRANT_COLLECTION_NAME')
        
        # Configure embeddings (usa el mismo modelo que el notebook de ingesta)
        embeddings_model = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
        logger.info(f"[Qdrant] Using embeddings model: {embeddings_model}")
        embeddings = OpenAIEmbeddings(model=embeddings_model)
        
        # Configure Qdrant client
        if qdrant_url:
            logger.info(f"[Qdrant] URL: {qdrant_url} | Collection: {collection_name}")
            client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_key
            )
        else:
            client = QdrantClient(":memory:")  # In-memory client for testing
        
        self.qdrant_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings
        )
        
        # Create retriever
        self.retriever = self.qdrant_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
    
    def setup_classifiers(self):
        """Setup complexity classifier and tool router"""
        
        # Complexity Classifier
        complexity_prompt = PromptTemplate(template=COMPLEXITY_PROMPT, input_variables=["question"])
        self.complexity_classifier = (
            complexity_prompt 
            | self.llm_json.with_structured_output(ComplexityLevel)
        )

        # Tool Router
        tool_router_prompt = PromptTemplate(template=TOOL_ROUTER_PROMPT, input_variables=["question"])
        self.tool_router = (
            tool_router_prompt 
            | self.llm_json.with_structured_output(ToolSelection)
        )
    
    def format_docs(self, docs):
        """Format documents for RAG context"""
        return "\n\n".join(doc.page_content for doc in docs)
        
    def _build_graph(self):
        """Build the adaptive RAG graph with AdaptiveAgentState"""
        
        def classify_complexity(state: AdaptiveAgentState):
            """Classify question complexity based on last human message"""
            logger.info("---CLASSIFY COMPLEXITY---")
            
            # Extraer la última pregunta del usuario de los mensajes
            last_human_message = None
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    last_human_message = msg.content
                    break
            
            if not last_human_message:
                # Si no hay mensaje humano, usar mensaje por defecto
                complexity_level = "simple"
            else:
                result = self.complexity_classifier.invoke({"question": last_human_message})
                complexity_level = result.complexity_level
            
            logger.info(f"Complexity Level: {complexity_level}")
            # Retornar el estado actualizado con el nivel de complejidad
            return {
                "complexity_level": complexity_level,
                "retrieved_docs": state.get("retrieved_docs", None)
            }
        
        def simple_response(state: AdaptiveAgentState):
            """Generate simple response using full chat history"""
            logger.info("---SIMPLE RESPONSE---")

            # Prepend a system message and pass the full history to the chat model
            messages_for_model: List[BaseMessage] = [
                SystemMessage(content=SIMPLE_PROMPT)
            ] + self._get_last_messages(state)

            response = self.llm.invoke(messages_for_model)
            return {"messages": [response]}
        
        def rag_retrieve(state: AdaptiveAgentState):
            """Retrieve documents for RAG"""
            logger.info("---RAG RETRIEVE---")
            
            # Extraer la última pregunta
            last_human_message = None
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    last_human_message = msg.content
                    break
            
            # Recuperar documentos
            logger.info(f"Recuperando contexto de pregunta: {last_human_message}")
            documents = self.retriever.get_relevant_documents(last_human_message)

            logger.debug(f"[RAG] Docs recuperados: {len(documents)}")
            for i, doc in enumerate(documents):
                preview = doc.page_content.replace('\n',' ')[:220]
                logger.debug(f"[{i}] {preview}")
                logger.debug(f"    meta: {doc.metadata}")

            # Retornar estado actualizado con documentos
            return {
                "retrieved_docs": documents
            }
        
        def rag_generate(state: AdaptiveAgentState):
            """Generate RAG response using full chat history + context"""
            logger.info("---RAG GENERATE---")

            # Obtener documentos recuperados
            documents = state.get("retrieved_docs", [])
            context_text = self.format_docs(documents) if documents else ""

            # Prepend system with instructions and context, then pass full history
            system_content = f"{RAG_PROMPT}\n\nContexto:\n{context_text}"
            messages_for_model: List[BaseMessage] = [
                SystemMessage(content=system_content)
            ] + self._get_last_messages(state)

            response = self.llm.invoke(messages_for_model)
            return {"messages": [response]}
        
        def call_model_with_tools(state: AdaptiveAgentState):
            """Call model with tools for complex queries"""
            logger.info("---CALL MODEL WITH TOOLS---")
            
            # Usar el modelo con los últimos 10 mensajes
            response = self.model.invoke(self._get_last_messages(state))
            
            # Devolver solo el delta de mensajes
            return {
                "messages": [response]
            }
        
        def route_by_complexity(state: AdaptiveAgentState):
            """Route based on complexity classification"""
            complexity_level = state.get("complexity_level", "simple")
            logger.info(f"---ROUTE BY COMPLEXITY: {complexity_level}---")
            return complexity_level

        # Define the graph
        builder = StateGraph(AdaptiveAgentState)
        
        # Add nodes
        builder.add_node("classify_complexity", classify_complexity)
        builder.add_node("simple_response", simple_response)
        builder.add_node("rag_retrieve", rag_retrieve)
        builder.add_node("rag_generate", rag_generate)
        builder.add_node("call_model_with_tools", call_model_with_tools)
        builder.add_node(
            "tools",
            ToolNode([registrar_cliente, contar_registros, get_current_date, get_program_price])
        )

        # Add edges
        builder.add_edge(START, "classify_complexity")
        
        # Conditional routing from complexity classifier
        builder.add_conditional_edges(
            "classify_complexity",
            route_by_complexity,
            {
                "simple": "simple_response",
                "rag": "rag_retrieve", 
                "tools": "call_model_with_tools",
            },
        )
        
        # Simple path
        builder.add_edge("simple_response", END)
        
        # RAG path
        builder.add_edge("rag_retrieve", "rag_generate")
        builder.add_edge("rag_generate", END)
        
        # Tools path
        builder.add_conditional_edges(
            "call_model_with_tools",
            tools_condition,
            {"tools": "tools", END: END}
        )
        builder.add_edge("tools", "call_model_with_tools")

        # Compile the graph con nombre estable para
        # asegurar que se recupere el estado tras reinicios
        graph_name = os.getenv("GRAPH_NAME", "chatbot_graph_v1")
        self.graph_name = graph_name
        return builder.compile(
            checkpointer=self.within_thread_memory,
            name=graph_name,
        )
    
    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": user_id, "user_id": user_id, "checkpoint_ns": self.graph_name}}
        input_messages = [HumanMessage(content=message)]
        
        # Inicializar el estado con todos los campos requeridos
        initial_state = {
            "messages": input_messages,
            "complexity_level": None,
            "retrieved_docs": None
        }
        
        result = self.graph.invoke(initial_state, config)
        ai_message = result["messages"][-1]
        
        return {
            "answer": ai_message.content,
            "user": user_id,
            "thread_id": user_id
        }
    
    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        thread = {"configurable": {"thread_id": user_id, "checkpoint_ns": self.graph_name}}
        state = self.graph.get_state(thread).values

        if not state:
            return []
        
        # Convertir los mensajes a un formato más simple para la API
        formatted_messages = []
        logger.info(f"Chat history: {state['messages']}")
        for m in state["messages"]:
            if isinstance(m, BaseMessage):
                message_data = {
                    "role": m.type,
                    "text": m.content  # Valor por defecto
                }
                
                # Caso especial para AIMessage con tool_calls
                if isinstance(m, AIMessage) and hasattr(m, 'tool_calls') and m.tool_calls:
                    tool_calls_content = []
                    for tool_call in m.tool_calls:
                        tool_info = {
                            "tool_name": tool_call.get("name", ""),
                            "parameters": tool_call.get("args", {})
                        }
                        tool_calls_content.append(tool_info)
                    
                    # Si hay tool_calls, sobrescribimos el content
                    message_data["content"] = {
                        "tool_calls": tool_calls_content,
                        "original_content": m.content  # Mantenemos el original por si acaso
                    }
                
                formatted_messages.append(message_data)
        
        return formatted_messages
