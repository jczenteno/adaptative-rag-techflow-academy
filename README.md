# Adaptive-RAG Demo - TechFlow Academy

## 📋 Descripción

Sistema de **Adaptive Retrieval-Augmented Generation (Adaptive-RAG)** implementado como demo del paper ["Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity"](https://arxiv.org/pdf/2403.14403). El sistema automatiza la atención al cliente de **TechFlow Academy** a través de WhatsApp, adaptando dinámicamente su estrategia de respuesta según la complejidad de las consultas estudiantiles.

## 🧠 Innovación: Adaptive-RAG

### ¿Qué es Adaptive-RAG?
A diferencia del RAG tradicional que siempre busca en la base de conocimiento, **Adaptive-RAG** clasifica inteligentemente las preguntas por complejidad y decide la estrategia óptima:

- **Consultas Simples**: Respuesta directa del LLM (sin retrieval)
- **Consultas Moderadas**: RAG estándar con búsqueda semántica
- **Consultas Complejas**: RAG iterativo con múltiples búsquedas y herramientas

### Ventajas del Enfoque Adaptativo
- ⚡ **Mayor Eficiencia**: Evita búsquedas innecesarias para preguntas simples
- 🎯 **Mejor Precisión**: Estrategias especializadas según complejidad
- 💰 **Menor Costo**: Reduce llamadas a APIs de embedding y búsqueda
- 🚀 **Mejor UX**: Respuestas más rápidas y precisas

## 📱 Integración WhatsApp Business

### Canal Principal de Comunicación
El sistema utiliza **WAHA (WhatsApp HTTP API)** para proporcionar atención 24/7 a través de WhatsApp Business, el canal preferido por estudiantes latinoamericanos.

### Características WhatsApp
- **Respuestas Instantáneas**: Latencia promedio < 3 segundos
- **Multimedia Support**: Envío de PDFs, imágenes y documentos
- **Estado de Lectura**: Confirmación de entrega y lectura
- **Conversaciones Contextuales**: Mantiene historial de chat

## 🚀 Funcionalidades Principales

### 1. Clasificador de Complejidad
- **ML Classifier**: Determina la complejidad de cada consulta
- **Routing Inteligente**: Dirige a la estrategia RAG apropiada
- **Learning Continuo**: Mejora clasificación con feedback de usuarios

### 2. Estrategias RAG Adaptativas

#### 🟢 Nivel 1: Respuesta Directa
```
Consulta: "Hola, ¿están abiertos?"
Estrategia: LLM directo (sin búsqueda)
Tiempo: ~0.5s
```

#### 🟡 Nivel 2: RAG Estándar  
```
Consulta: "¿Qué incluye el programa de Data Engineering?"
Estrategia: Búsqueda semántica + generación
Tiempo: ~2s
```

#### 🔴 Nivel 3: RAG Iterativo + Tools
```
Consulta: "Quiero comparar costos, modalidades y testimonios de graduados entre Data Engineering y ML Engineer para decidir cuál tomar"
Estrategia: Múltiples búsquedas + herramientas + síntesis
Tiempo: ~5s
```

### 3. Herramientas Especializadas (Tools)
- **Consulta de Precios**: Acceso en tiempo real a costos desde base de datos
- **Estadísticas de Inscripción**: Información actualizada sobre cupos disponibles
- **Registro de Interés**: Captura leads y programa callbacks
- **Generación de PDFs**: Envía brochures personalizados por WhatsApp

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   WAHA API      │    │  Complexity     │
│   Business      │◄──►│   Gateway       │◄──►│  Classifier     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────▼─────────┐
                                               │  Adaptive Router  │
                                               └─────────┬─────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    │                                    │                                    │
           ┌─────────▼─────────┐              ┌─────────▼─────────┐                ┌─────────▼─────────┐
           │   Direct LLM      │              │   Standard RAG    │                │  Iterative RAG    │
           │   (Simple Q's)    │              │   (Moderate Q's)  │                │   (Complex Q's)   │
           └───────────────────┘              └─────────┬─────────┘                └─────────┬─────────┘
                                                        │                                    │
                                              ┌─────────▼─────────┐                ┌─────────▼─────────┐
                                              │   Vector Store    │                │   Tools Engine    │
                                              │   (Embeddings)    │                │   + Vector Store  │
                                              └───────────────────┘                └───────────────────┘
```

## 📚 Base de Conocimiento - TechFlow Academy

### Programas Disponibles
- **Data Engineering** (6 meses) - Apache Spark, AWS, Docker
- **Data Architecture** (5 meses) - Enterprise Data Design, Cloud Architecture  
- **ML Engineering** (7 meses) - MLOps, Deep Learning, Computer Vision
- **Data Visualization** (4 meses) - Tableau, Power BI, D3.js
- **Marketing Analytics** (5 meses) - Google Analytics, Attribution Modeling

### Documentos Institucionales (9 archivos .md)
- **Cursos.md**: 30 cursos especializados con descripciones detalladas
- **Docentes.md**: 20+ instructores de empresas como Rappi, BCP, Globant
- **Matricula.md**: Proceso de admisión y financiamiento flexible
- **Horarios.md**: Modalidades virtual, presencial e híbrida
- **Reglamento.md**: Políticas académicas y normas de convivencia
- **Sedes.md**: 4 campus en Lima (Miraflores, San Isidro, La Molina, Surco)
- **FAQ.md**: 25+ preguntas frecuentes categorizadas
- **Empresas_Aliadas.md**: 120+ empresas partners (BCP, Yape, Mercado Libre)
- **Graduados.md**: Testimonios reales con incrementos salariales 180%+

## 💬 Ejemplos de Conversación WhatsApp

### Consulta Nivel 1 (Directa)
```
📱 Usuario: "Hola! Buenos días"
🤖 TechFlow: "¡Hola! 👋 Buen día. Soy el asistente de TechFlow Academy. 
¿En qué puedo ayudarte hoy? Puedo informarte sobre programas, costos, 
horarios y procesos de admisión."

📱 Usuario: "¿Están abiertos los sábados?"
🤖 TechFlow: "Sí, estamos abiertos los sábados de 8:00 AM a 8:00 PM 
para clases y laboratorios. Los domingos de 9:00 AM a 6:00 PM. 
¿Te interesa algún programa en particular?"
```

### Consulta Nivel 2 (RAG Estándar)
```
📱 Usuario: "¿Qué empresas contratan a sus graduados de Data Engineering?"
🤖 TechFlow: "Nuestros graduados de Data Engineering trabajan en empresas líderes como:

🏦 **Sector Financiero**: BCP, BBVA, Scotiabank, Yape
💼 **Tech & Startups**: Rappi, Mercado Libre, Globant  
🛒 **Retail**: Falabella, Linio, Plaza Vea

El 85% encuentra empleo en los primeros 6 meses con salarios desde S/4,000 para junior hasta S/9,500 para mid-level.

¿Te gustaría saber más sobre el programa o el proceso de admisión?"
```

### Consulta Nivel 3 (RAG Iterativo + Tools)
```
📱 Usuario: "Necesito comparar Data Engineering vs ML Engineer: costos, duración, empresas que contratan y testimonios de graduados para decidir cuál estudiar"

🤖 TechFlow: "Te ayudo con esa comparación completa 📊

**DATA ENGINEERING** 
⏱️ Duración: 6 meses
💰 Costo: S/3,500 (S/2,975 al contado)  
📈 Salario inicial: S/4,000-6,500
🏢 Empresas: BCP, Rappi, Scotiabank, AWS partners

**ML ENGINEER**
⏱️ Duración: 7 meses  
💰 Costo: S/4,200 (S/3,570 al contado)
📈 Salario inicial: S/4,500-7,000
🏢 Empresas: Yape, Mercado Libre, Globant, startups AI

**TESTIMONIOS DESTACADOS:**
👨‍💻 Diego (Data Eng): "Pasé de S/3,500 a S/8,000 en Rappi"
👩‍💻 Andrea (ML Eng): "PhD en Matemáticas, ahora Senior ML Engineer en MercadoLibre"

¿Te envío el brochure completo con detalles de ambos programas? 📄"

📱 Usuario: "Sí, envíamelo por favor"
🤖 TechFlow: "¡Perfecto! Te envío el PDF comparativo 📎 

[Envía PDF automáticamente]

También registré tu interés. ¿Te gustaría agendar una cita con un asesor académico para resolver dudas específicas?"
```

## 🛠️ Stack Tecnológico

### Core RAG
- **LLM**: OpenAI GPT-4 / Claude Sonnet
- **Embeddings**: OpenAI text-embedding-3-large
- **Vector DB**: Pinecone / Chroma / Qdrant
- **Framework**: LangChain / LlamaIndex

### Adaptive Logic
- **Classifier**: Fine-tuned BERT / RoBERTa para clasificación de complejidad
- **Router**: LangGraph para orchestración de estrategias
- **Metrics**: MLflow para tracking de performance

### WhatsApp Integration  
- **WAHA**: WhatsApp HTTP API para envío/recepción
- **Webhook Handler**: FastAPI para procesar mensajes
- **Media Storage**: AWS S3 para PDFs y documentos

### Backend & Database
- **API**: FastAPI con async support
- **Database**: PostgreSQL para datos transaccionales
- **Cache**: Redis para session management
- **Queue**: Celery para tareas asíncronas

## 📁 Estructura del Proyecto

```
adaptive-rag-techflow/
├── docs/                           # Base de conocimiento
│   ├── Cursos.md
│   ├── Matricula.md  
│   ├── [... 7 archivos más]
├── src/
│   ├── adaptive_rag/               # Motor Adaptive-RAG
│   │   ├── classifier.py           # Clasificador de complejidad
│   │   ├── router.py              # Router de estrategias
│   │   ├── strategies/            # Estrategias RAG
│   │   │   ├── direct_llm.py
│   │   │   ├── standard_rag.py
│   │   │   └── iterative_rag.py
│   │   └── evaluator.py           # Métricas y evaluación
│   ├── whatsapp/                  # Integración WhatsApp
│   │   ├── waha_client.py         # Cliente WAHA
│   │   ├── message_handler.py     # Procesador de mensajes
│   │   └── media_manager.py       # Gestión de archivos
│   ├── tools/                     # Herramientas especializadas
│   │   ├── pricing.py
│   │   ├── enrollment.py
│   │   ├── registration.py
│   │   └── pdf_generator.py       # Generación de brochures
│   ├── database/                  # Conexión a BD
│   │   ├── models.py
│   │   └── queries.py
│   └── api/                       # API endpoints
│       ├── main.py
│       └── webhooks.py            # Webhooks WhatsApp
├── models/                        # Modelos entrenados
│   ├── complexity_classifier.pkl
│   └── evaluation_metrics.json
├── config/                        # Configuraciones
│   ├── settings.py
│   └── waha_config.json
└── tests/                         # Tests
    ├── test_adaptive_rag.py
    ├── test_classifier.py
    └── test_whatsapp.py
```

## ⚙️ Configuración e Instalación

### Prerrequisitos
```bash
- Python 3.9+
- WhatsApp Business Account
- WAHA setup (Docker/Cloud)
- API Keys (OpenAI, Pinecone, etc.)
- PostgreSQL database
```

### 1. Configuración WAHA
```bash
# Docker setup para WAHA
docker run -it --rm -p 3000:3000/tcp devlikeapro/waha

# O usar WAHA Cloud (recomendado para producción)
```

### 2. Instalación Proyecto
```bash
# Clonar repositorio
git clone https://github.com/usuario/adaptive-rag-techflow.git
cd adaptive-rag-techflow

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con API keys y configuración WAHA

# Inicializar base de datos
python src/database/init_db.py

# Generar embeddings para base de conocimiento
python src/adaptive_rag/create_embeddings.py

# Entrenar clasificador de complejidad (opcional, incluimos pre-entrenado)
python src/adaptive_rag/train_classifier.py

# Configurar webhook de WhatsApp
python src/whatsapp/setup_webhook.py
```

### 3. Ejecutar Sistema
```bash
# Iniciar API server
python src/api/main.py

# En otra terminal, iniciar worker para tareas asíncronas
celery -A src.api.main worker --loglevel=info

# Verificar webhook WhatsApp
curl -X POST localhost:8000/webhook/whatsapp -H "Content-Type: application/json" -d '{"test": true}'
```

## 📊 Implementación del Paper

### Métricas de Evaluación
Siguiendo el paper original, evaluamos:

- **Accuracy**: Precisión del clasificador de complejidad
- **Efficiency**: Tiempo de respuesta por estrategia  
- **Cost**: Tokens consumidos y llamadas a APIs
- **Quality**: Relevancia y completitud de respuestas

### Dataset de Entrenamiento
- **Simple Questions**: 500 consultas de saludo, horarios, contacto
- **Moderate Questions**: 800 consultas sobre programas específicos
- **Complex Questions**: 300 consultas multi-facet que requieren synthesis

### Resultados Esperados
Basado en el paper, esperamos:
- 40% reducción en costo computacional
- 60% mejora en tiempo de respuesta para consultas simples
- Mantenimiento de calidad en respuestas complejas

## 🚀 Roadmap

- [x] **v0.1**: RAG básico + clasificador de complejidad
- [x] **v0.2**: Integración WAHA + WhatsApp Business  
- [ ] **v0.3**: Herramientas especializadas + generación PDF
- [ ] **v0.4**: Fine-tuning del clasificador con datos reales
- [ ] **v1.0**: Sistema completo con métricas del paper
- [ ] **v1.1**: Dashboard analytics + A/B testing
- [ ] **v1.2**: Multi-idioma + integración CRM

## 📈 Métricas en Tiempo Real

### Dashboard Administrativo
- Volumen de consultas por hora/día
- Distribución de complejidad de preguntas
- Tiempo promedio de respuesta por estrategia
- Tasa de conversión (consulta → registro de interés)
- Satisfacción del usuario (ratings por WhatsApp)

### Análisis de Performance
- Precisión del clasificador por tipo de consulta
- Costo por respuesta (tokens + API calls)
- Casos donde el router falla y requiere intervención humana

## 📞 Demo y Contacto

### Probar el Sistema
- **WhatsApp Demo**: +51 999 XXX XXX
- **Web Interface**: [demo.techflow.academy](http://demo.techflow.academy)
- **Video Demo**: [YouTube](https://youtube.com/watch?v=xxx)

### Paper Implementation
- **Paper Original**: [Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity](https://arxiv.org/pdf/2403.14403)
- **Nuestra Implementación**: Adaptación para dominio educativo + WhatsApp
- **Resultados**: Blog post con findings y métricas comparativas

### Contacto
- **Desarrollador**: [Tu Nombre]
- **Email**: tu.email@ejemplo.com  
- **LinkedIn**: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- **Paper Authors**: Citación y agradecimientos en implementación

---

> 💡 **Nota**: Esta es una implementación de investigación/demo del paper Adaptive-RAG aplicado al dominio educativo. El objetivo es mostrar las ventajas del enfoque adaptativo en un caso de uso real con integración WhatsApp Business.

```
---
config:
  flowchart:
    curve: linear
  layout: dagre
---
flowchart TD
    start(["\_\_start\_\_"]) --> classify_complexity("classify_complexity")
    classify_complexity -.-> simple_response("simple_response") & rag_retrieve("rag_retrieve") & call_model_with_tools("call_model_with_tools")
    
    %% Simple path
    simple_response --> tend(["\_\_end\_\_"])
    
    %% RAG Adaptativo path - Primera evaluación (documentos)
    rag_retrieve --> grade_documents("grade_documents")
    grade_documents -.-> rag_generate("rag_generate") & rewrite_question("rewrite_question") & web_search_fallback("web_search_fallback")
    
    %% Primer bucle de reescritura (documentos irrelevantes)
    rewrite_question --> rag_retrieve
    
    %% Generar respuesta y segunda evaluación (calidad de respuesta)
    rag_generate --> evaluate_answer("evaluate_answer")
    evaluate_answer -.-> tend & rewrite_question
    
    %% Fallback path cuando documentos fallan repetidamente
    web_search_fallback --> tend
    
    %% Tools path
    call_model_with_tools -.-> tend & tools("tools")
    tools --> call_model_with_tools
    
    %% Apply styles
    classify_complexity:::default
    simple_response:::default
    rag_retrieve:::default
    grade_documents:::default
    rag_generate:::default
    evaluate_answer:::default
    rewrite_question:::default
    web_search_fallback:::default
    call_model_with_tools:::default
    tools:::default
    
    classDef default fill:transparent ,stroke:#B388FF ,stroke-width:2px,color:#000000
    classDef startClass fill:#000000,stroke:#B388FF ,stroke-width:2px,color:#000000
    classDef tendClass fill:#BFB6FC ,stroke:#B388FF ,stroke-width:2px,color:#000000
    
    style start fill:#FFFFFF
    style classify_complexity fill:#F3EEFF
    style simple_response fill:#F3EEFF
    style rag_retrieve fill:#F3EEFF
    style grade_documents fill:#F3EEFF
    style rag_generate fill:#F3EEFF
    style evaluate_answer fill:#F3EEFF
    style rewrite_question fill:#F3EEFF
    style web_search_fallback fill:#F3EEFF
    style call_model_with_tools fill:#F3EEFF
    style tools fill:#F3EEFF
    style tend fill:#bfb6fc
```