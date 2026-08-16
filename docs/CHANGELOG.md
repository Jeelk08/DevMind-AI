# Changelog

All notable changes to DevMind AI will be documented in this file.

---

## v0.1.0

### Added

- FastAPI Backend
- Layered Architecture
- Chat API
- AI Service
- DevMind Agent
- Gemini Integration
- DevMind Personality v1.0
- Version Management
- Architecture Documentation
- Product Roadmap

---


# v0.2.0

## Added

- Conversation Memory
- Session Management
- Memory Manager
- DevMind Agent orchestration
- Multi-turn AI conversations

## Tested

- Session creation
- Message persistence
- History retrieval
- Context-aware responses



# v0.3.0 - Tool Calling Framework

## 🚀 Added

### Tool Framework
- Added `BaseTool` abstract contract.
- Added `ToolRequest` and `ToolResponse` models.
- Added `ToolRegistry` for tool registration and lookup.
- Added `ToolExecutor` to execute registered tools.
- Added initial `Planner` component.

### Memory Tool
- Added `MemoryTool` implementing the BaseTool interface.
- Connected MemoryTool to MemoryManager.
- Added support for retrieving conversation history through the tool framework.

### DevMind Agent
- Refactored `DevMindAgent` into an orchestrator.
- Integrated:
  - Planner
  - Tool Registry
  - Tool Executor
  - Memory Tool
- Added fallback behavior when no tool is required.

## 🏗 Architecture

The agent now follows a tool execution pipeline:

User
→ DevMindAgent
→ Planner
→ ToolRequest
→ ToolExecutor
→ ToolRegistry
→ Tool
→ ToolResponse
→ AIService
→ User

## ✅ Result

- First end-to-end tool execution pipeline completed.
- Framework is now extensible for future tools such as:
  - Git Tool
  - Repository Tool
  - Web Search Tool
  - RAG Tool


  

# v0.3.0 - Tool Calling Framework

## Added

- BaseTool abstraction
- ToolRegistry
- ToolExecutor
- Planner
- ToolRequest
- ToolResponse
- MemoryTool

## Changed

- DevMindAgent now acts as the system orchestrator.
- Memory access is now performed through the tool framework.
- Chat flow updated to support tool execution before AI generation.

## Architecture

- Introduced modular tool-calling pipeline.
- Separated planning from execution.
- Established foundation for future tools and intelligent planning.


# v0.4.0 - Project Knowledge Engine

## Added

- RepositoryLoader for project file discovery
- FileFilter for indexing supported source files
- GenericChunker for splitting project files into chunks
- GeminiEmbeddingService for semantic embeddings
- InMemoryVectorStore for vector storage
- ProjectIndexer for repository indexing
- SimpleRetriever for semantic search
- Project Knowledge domain models
- Integration test for the complete RAG pipeline

## Result

DevMind can now index its own source code and retrieve semantically relevant code snippets from the repository.


# v0.5.0 - Repository Intelligence
## Added

### Repository Intelligence
- Introduced the Repository Intelligence module for structural code analysis.
- Added RepositoryAnalysis as the central analysis model.
- Added RepositoryMetadata for repository-level information.
- Added Symbol, ImportStatement, Relationship, and SymbolDependency models.

### AST Processing
- Implemented ASTExtractor to parse Python source files into ASTs.
- Added ParsedFile model to store ProjectFile and parsed AST together.
- Added graceful error handling for files that fail parsing.

### Symbol Extraction
- Implemented SymbolExtractor using the Visitor pattern.
- Added SymbolVisitor to discover:
  - Classes
  - Functions
  - Methods
- Added unique symbol identification.
- Added parent-child symbol tracking.

### Import Analysis
- Implemented ImportExtractor.
- Added ImportVisitor to collect:
  - import statements
  - from ... import ... statements

### Relationship Analysis
- Implemented RelationshipGraph.
- Added support for DEFINES relationships between parent and child symbols.

### Analyzer
- Added PythonRepositoryAnalyzer to orchestrate:
  - AST extraction
  - Symbol extraction
  - Import extraction
  - Relationship graph construction

### Architecture Improvements
- Refactored RepositoryLoader to return ProjectFile objects directly.
- Simplified ProjectIndexer by removing ProjectFile creation responsibility.
- Continued use of Constructor Injection across Repository Intelligence components.

### Testing
- Added end-to-end Repository Intelligence integration test.
- Successfully analyzed DevMind AI's own repository.

---

## 📊 Repository Analysis Result

Repository Intelligence successfully analyzed the DevMind AI source code.

- Files Analysed: 60
- Symbols Found: 138
- Imports Found: 176
- Relationships Found: 81



# v0.6.0 - Repository Intelligence Expansion

## Added

### Relationship Graph
- Expanded `RelationshipGraph` to support:
  - DEFINES relationships
  - INHERITS relationships
  - CALLS relationships
  - IMPORTS relationships
- Added modular relationship graph builders.
- Added symbol resolvers for relationship construction.
- Added `GraphQuery` for querying repository relationships.

### Repository Context
- Added `RepositoryContextTool`.
- Integrated semantic RAG retrieval with Repository Intelligence.
- Added repository-aware context generation combining:
  - Relevant code chunks
  - Repository symbols
  - Structural relationships

### Agent Integration
- Integrated `RepositoryContextTool` into `DevMindAgent`.
- Extended `Planner` to recognize repository-related requests.
- Repository-aware queries can now be handled through the `/chat` API.

### API
- Updated `ChatRequest` to support optional session creation.
- Updated `ChatResponse` to return the generated session ID.

## Improved

- Refactored `RelationshipGraph` into smaller components following the Single Responsibility Principle.
- Updated Gemini integration to use the current `google-genai` client API.

## Tested

- Repository Intelligence end-to-end pipeline.
- Relationship graph generation.
- Repository context integration.
- Full pytest suite.
- End-to-end repository-aware interaction through the FastAPI `/chat` endpoint.

## Known Limitations

- Repository Context currently relies on semantic top-k retrieval and may not always retrieve an exact requested file for highly specific queries.
- Repository analysis is currently performed sequentially during Repository Context execution.

## Result

DevMind can now combine semantic code retrieval with structural repository intelligence to provide repository-aware responses.


## [0.7.0] - Intelligent Repository Retrieval

### Added
- Implemented intelligent repository retrieval combining:
  - Semantic retrieval
  - Symbol-based retrieval
  - Path-based retrieval
- Added `RetrievalCandidate` model for unified retrieval candidates.
- Added chunk-level candidate identification using file path and chunk offsets.
- Added relevance scoring with semantic, symbol, and path signals.
- Added ranking of retrieval candidates based on final relevance score.

### Improved
- Improved IntelligentRetriever candidate handling.
- Preserved multiple chunks from the same file when they represent different regions.
- Improved prioritization of symbol and path matches over purely semantic matches.
- Fixed handling of `Chunk` and `SearchResult` objects during semantic retrieval.

### Testing
- Added and updated IntelligentRetriever tests.
- Added retrieval ranking tests covering:
  - Semantic score ranking
  - Symbol match prioritization
  - Path match prioritization
  - Combined retrieval signals
- Current test status: 16 passed, 1 failure caused by Gemini embedding API quota exhaustion.

## Next


🚧 v0.7.0 — Repository Intelligence Expansion


Status

Current Stable Development Version