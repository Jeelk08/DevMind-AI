```mermaid
graph TD

    FE[Frontend]
    API[FastAPI API]
    AGENT[DevMindAgent]

    MM[MemoryManager]
    AI[AIService]

    CS[ConversationStore]
    SM[SessionManager]

    DB[(SQLite)]
    GEMINI[Gemini API]

    FE --> API
    API --> AGENT

    AGENT --> MM
    AGENT --> AI

    MM --> CS
    MM --> SM

    CS --> DB
    SM --> DB

    AI --> GEMINI
```