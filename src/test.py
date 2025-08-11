"""
Adaptive RAG Implementation for TechFlow Academy
Based on: https://arxiv.org/pdf/2403.14403

3-Level Adaptive Strategy:
- Level 1 (Simple): Direct LLM response with system prompt
- Level 2 (RAG): Vector search + generation  
- Level 3 (Tools): Specialized tools + generation
"""

import os
from typing import List, Dict, Any
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from langgraph.graph import END, StateGraph, START


class GraphState(TypedDict):
    """
    Represents the state of our adaptive RAG graph.
    
    Attributes:
        question: User question
        generation: LLM generation
        documents: Retrieved documents
        complexity_level: Determined complexity (simple, rag, tools)
        tool_name: Selected tool name for tools level
        tool_result: Result from tool execution
    """
    question: str
    generation: str
    documents: List[str]
    complexity_level: str
    tool_name: str
    tool_result: str


class AdaptiveRAGTechFlow:
    """
    Adaptive RAG system for TechFlow Academy with 3-level routing strategy
    """
    
    def __init__(self):
        self.setup_llm()
        self.setup_qdrant()
        self.setup_classifiers()
        self.setup_tools()
        self.build_graph()
    
    def setup_llm(self):
        """Configure OpenAI LLM"""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )
        
        self.llm_json = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0
        )
    
    def setup_qdrant(self):
        """Setup Qdrant vector store (using your existing configuration)"""
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_key = os.getenv('QDRANT_KEY')
        collection_name = os.getenv('QDRANT_COLLECTION_NAME')
        
        # Configure embeddings
        embeddings = OpenAIEmbeddings()
        
        # Configure Qdrant client
        if qdrant_url:
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
            search_kwargs={"k": 5}
        )
    
    def setup_classifiers(self):
        """Setup complexity classifier and tool router"""
        
        # Complexity Classifier
        complexity_prompt = PromptTemplate(
            template="""Eres un experto clasificando la complejidad de preguntas de estudiantes de TechFlow Academy.

Clasifica la pregunta en uno de estos 3 niveles:

SIMPLE: Saludos, consultas básicas sobre horarios, ubicación, contacto, despedidas
- Ejemplos: "Hola", "¿Están abiertos?", "¿Dónde quedan?", "Gracias", "Adiós"

RAG: Preguntas sobre programas, cursos, profesores, metodología, contenido académico
- Ejemplos: "¿Qué incluye Data Engineering?", "¿Quién enseña ML?", "¿Cómo son las clases?"

TOOLS: Preguntas sobre costos, inscripciones, disponibilidad de cupos, registro
- Ejemplos: "¿Cuánto cuesta?", "¿Hay cupos en Data Science?", "Quiero inscribirme"

Retorna JSON con clave 'complexity_level' y valor 'simple', 'rag' o 'tools'.

Pregunta: {question}""",
            input_variables=["question"],
        )
        
        self.complexity_classifier = (
            complexity_prompt 
            | self.llm_json.with_structured_output({"complexity_level": str})
        )
        
        # Tool Router
        tool_router_prompt = PromptTemplate(
            template="""Eres un router que determina qué herramienta usar según la pregunta del estudiante.

Herramientas disponibles:
- get_course_cost: Para preguntas sobre precios, costos, valores de programas
- get_student_count: Para preguntas sobre cuántos estudiantes, disponibilidad, cupos
- register_student: Para inscripciones, registros, matriculas

Ejemplos:
"¿Cuánto cuesta Data Engineering?" → get_course_cost
"¿Hay cupos disponibles?" → get_student_count  
"Quiero inscribirme en ML Engineer" → register_student

Retorna JSON con clave 'tool_name' y el nombre de la herramienta.

Pregunta: {question}""",
            input_variables=["question"],
        )
        
        self.tool_router = (
            tool_router_prompt 
            | self.llm_json.with_structured_output({"tool_name": str})
        )
    
    def setup_tools(self):
        """Setup tool functions (placeholders for implementation)"""
        
        def get_course_cost(course_name: str) -> str:
            """
            Get cost information for a specific course/program
            
            Args:
                course_name: Name of the course/program
                
            Returns:
                Cost information as string
            """
            # TODO: Implement database query for course costs
            return f"Información de costo para {course_name} - [PLACEHOLDER - IMPLEMENTAR]"
        
        def get_student_count(program_name: str) -> str:
            """
            Get current student enrollment count for a program
            
            Args:
                program_name: Name of the program
                
            Returns:
                Student count information as string
            """
            # TODO: Implement database query for student counts
            return f"Información de estudiantes registrados en {program_name} - [PLACEHOLDER - IMPLEMENTAR]"
        
        def register_student(student_info: Dict[str, Any]) -> str:
            """
            Register student interest or enrollment
            
            Args:
                student_info: Dictionary with student information
                
            Returns:
                Registration confirmation as string
            """
            # TODO: Implement student registration logic
            return f"Registro de estudiante procesado - [PLACEHOLDER - IMPLEMENTAR]"
        
        self.tools = {
            "get_course_cost": get_course_cost,
            "get_student_count": get_student_count,
            "register_student": register_student
        }
    
    def format_docs(self, docs):
        """Format documents for RAG context"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def build_graph(self):
        """Build the adaptive RAG graph"""
        
        # Create workflow
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("classify_complexity", self.classify_complexity)
        workflow.add_node("simple_response", self.simple_response)
        workflow.add_node("rag_retrieve", self.rag_retrieve)
        workflow.add_node("rag_generate", self.rag_generate)
        workflow.add_node("route_tool", self.route_tool)
        workflow.add_node("execute_tool", self.execute_tool)
        workflow.add_node("tool_generate", self.tool_generate)
        
        # Add edges
        workflow.add_edge(START, "classify_complexity")
        
        # Conditional routing from complexity classifier
        workflow.add_conditional_edges(
            "classify_complexity",
            self.route_by_complexity,
            {
                "simple": "simple_response",
                "rag": "rag_retrieve", 
                "tools": "route_tool",
            },
        )
        
        # Simple path
        workflow.add_edge("simple_response", END)
        
        # RAG path
        workflow.add_edge("rag_retrieve", "rag_generate")
        workflow.add_edge("rag_generate", END)
        
        # Tools path
        workflow.add_edge("route_tool", "execute_tool")
        workflow.add_edge("execute_tool", "tool_generate")
        workflow.add_edge("tool_generate", END)
        
        # Compile graph
        self.app = workflow.compile()
    
    # Node functions
    def classify_complexity(self, state):
        """Classify question complexity"""
        print("---CLASSIFY COMPLEXITY---")
        question = state["question"]
        
        result = self.complexity_classifier.invoke({"question": question})
        complexity_level = result["complexity_level"]
        
        print(f"Complexity Level: {complexity_level}")
        return {"question": question, "complexity_level": complexity_level}
    
    def simple_response(self, state):
        """Generate simple response using system prompt"""
        print("---SIMPLE RESPONSE---")
        question = state["question"]
        
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente amigable de TechFlow Academy, un instituto de programación y ciencia de datos en Lima, Perú.

Para consultas simples como saludos, ubicación, horarios básicos, contacto:
- Responde de forma cordial y directa
- Menciona que TechFlow Academy es especialista en Data Engineering, ML Engineering, Data Visualization, etc.
- Para consultas específicas sobre programas, costos o inscripciones, indica que puedes ayudar con información detallada
- Mantén un tono profesional pero cercano

Información básica:
- Horarios: Lunes a viernes 7AM-10PM, Sábados 8AM-8PM
- Sedes: Miraflores, San Isidro, La Molina, Surco
- Modalidades: Virtual, Presencial, Híbrida
- WhatsApp: Canal principal de comunicación"""),
            ("human", "{question}")
        ])
        
        chain = simple_prompt | self.llm | StrOutputParser()
        generation = chain.invoke({"question": question})
        
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "generation": generation
        }
    
    def rag_retrieve(self, state):
        """Retrieve documents for RAG"""
        print("---RAG RETRIEVE---")
        question = state["question"]
        
        documents = self.retriever.get_relevant_documents(question)
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "documents": documents
        }
    
    def rag_generate(self, state):
        """Generate RAG response"""
        print("---RAG GENERATE---")
        question = state["question"]
        documents = state["documents"]
        
        # RAG template
        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente especializado de TechFlow Academy. 

Responde la pregunta basándote únicamente en el contexto proporcionado sobre nuestros programas, profesores, metodología y servicios.

Instrucciones:
- Usa solo la información del contexto
- Si no encuentras información específica, indica que puedes ayudar de otra manera
- Mantén respuestas claras y estructuradas
- Incluye detalles relevantes como duración, modalidades, requisitos
- Sugiere próximos pasos cuando sea apropiado (ej: "¿Te gustaría conocer los costos?")"""),
            ("human", """Contexto:
{context}

Pregunta: {question}""")
        ])
        
        # Create RAG chain
        rag_chain = (
            {"context": lambda x: self.format_docs(x["documents"]), "question": lambda x: x["question"]}
            | rag_prompt
            | self.llm
            | StrOutputParser()
        )
        
        generation = rag_chain.invoke({
            "documents": documents,
            "question": question
        })
        
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "documents": documents,
            "generation": generation
        }
    
    def route_tool(self, state):
        """Route to appropriate tool"""
        print("---ROUTE TOOL---")
        question = state["question"]
        
        result = self.tool_router.invoke({"question": question})
        tool_name = result["tool_name"]
        
        print(f"Selected Tool: {tool_name}")
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "tool_name": tool_name
        }
    
    def execute_tool(self, state):
        """Execute selected tool"""
        print("---EXECUTE TOOL---")
        question = state["question"]
        tool_name = state["tool_name"]
        
        # Extract parameters from question (simplified)
        # TODO: Implement proper parameter extraction
        if tool_name == "get_course_cost":
            # Extract course name from question
            tool_result = self.tools[tool_name]("Data Engineering")  # Placeholder
        elif tool_name == "get_student_count":
            # Extract program name from question
            tool_result = self.tools[tool_name]("ML Engineer")  # Placeholder
        elif tool_name == "register_student":
            # Extract student info from question
            tool_result = self.tools[tool_name]({"name": "Usuario"})  # Placeholder
        else:
            tool_result = "Herramienta no disponible"
        
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "tool_name": tool_name,
            "tool_result": tool_result
        }
    
    def tool_generate(self, state):
        """Generate response based on tool result"""
        print("---TOOL GENERATE---")
        question = state["question"]
        tool_result = state["tool_result"]
        
        tool_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente de TechFlow Academy especializado en información sobre costos, inscripciones y disponibilidad.

Genera una respuesta natural y útil basada en el resultado de la herramienta consultada.

Instrucciones:
- Presenta la información de forma clara y estructurada
- Incluye próximos pasos o acciones recomendadas
- Mantén tono profesional pero amigable
- Si es información de costos, menciona opciones de financiamiento
- Si es sobre disponibilidad, sugiere alternativas si es necesario
- Si es registro, confirma y explica siguientes pasos"""),
            ("human", """Pregunta original: {question}

Resultado de consulta: {tool_result}

Genera una respuesta natural basada en esta información:""")
        ])
        
        chain = tool_prompt | self.llm | StrOutputParser()
        generation = chain.invoke({
            "question": question,
            "tool_result": tool_result
        })
        
        return {
            "question": question,
            "complexity_level": state["complexity_level"],
            "tool_name": state["tool_name"],
            "tool_result": tool_result,
            "generation": generation
        }
    
    # Edge functions
    def route_by_complexity(self, state):
        """Route based on complexity classification"""
        complexity_level = state["complexity_level"]
        print(f"---ROUTE BY COMPLEXITY: {complexity_level}---")
        return complexity_level
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Main query method for the adaptive RAG system
        
        Args:
            question: User question
            
        Returns:
            Final state with generation and metadata
        """
        inputs = {"question": question}
        
        # Run the graph
        final_state = None
        for output in self.app.stream(inputs):
            for key, value in output.items():
                print(f"Node '{key}' completed")
                final_state = value
        
        return final_state


# Usage Example
if __name__ == "__main__":
    # Initialize system
    adaptive_rag = AdaptiveRAGTechFlow()
    
    # Test different complexity levels
    test_questions = [
        "Hola, ¿cómo están?",  # Simple
        "¿Qué incluye el programa de Data Engineering?",  # RAG
        "¿Cuánto cuesta el programa de ML Engineer?",  # Tools
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"PREGUNTA: {question}")
        print('='*50)
        
        result = adaptive_rag.query(question)
        
        print(f"\nRESULTADO:")
        print(f"Complejidad: {result.get('complexity_level', 'N/A')}")
        print(f"Respuesta: {result.get('generation', 'N/A')}")
        print(f"Tool usado: {result.get('tool_name', 'N/A')}")