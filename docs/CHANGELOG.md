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


## Next

- v0.5 RAG implementation 


Status

Current Stable Development Version