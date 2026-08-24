import { useState } from "react";
import { sendChatMessage } from "../api/client";

const conversationMessages = {
  "conv-1": [
    {
      id: 101,
      role: "user",
      content: "How does the ProjectIndexer work?",
    },
    {
      id: 102,
      role: "assistant",
      content:
        "ProjectIndexer connects the repository loader, chunker, embedding service, and vector store into a single indexing pipeline. It loads project files, creates chunks, generates embeddings, and stores the embedded chunks for retrieval.",
    },
  ],

  "conv-2": [
    {
      id: 201,
      role: "user",
      content: "How does the ToolRegistry work?",
    },
    {
      id: 202,
      role: "assistant",
      content:
        "The ToolRegistry stores registered tools and allows DevMind to retrieve a tool by its unique ID before execution.",
    },
  ],

  "conv-3": [
    {
      id: 301,
      role: "user",
      content: "How does the Gemini client work?",
    },
    {
      id: 302,
      role: "assistant",
      content:
        "The Gemini client provides the AI and embedding services used by DevMind to generate responses and project knowledge embeddings.",
    },
  ],
};

const MESSAGES_STORAGE_KEY =
  "devmind-conversation-messages";

function loadSavedMessages() {
  const saved = localStorage.getItem(
    MESSAGES_STORAGE_KEY
  );

  if (!saved) {
    return conversationMessages;
  }

  try {
    return JSON.parse(saved);
  } catch {
    return conversationMessages;
  }
}

function useChat() {
  const [messages, setMessages] = useState([]);

  const [isProcessing, setIsProcessing] =
    useState(false);

  const [chatError, setChatError] =
    useState(null);

  const [failedMessage, setFailedMessage] =
    useState(null);

  const [savedMessages, setSavedMessages] =
    useState(loadSavedMessages);

  const clearMessages = () => {
    setMessages([]);
    setIsProcessing(false);
    setChatError(null);
    setFailedMessage(null);
  };

  const loadMessages = (
    conversationId
  ) => {
    const conversation =
      savedMessages[conversationId] || [];

    setMessages([...conversation]);
    setIsProcessing(false);
    setChatError(null);
    setFailedMessage(null);
  };

  const saveMessages = (
    conversationId,
    newMessages
  ) => {
    setSavedMessages((current) => {
      const updated = {
        ...current,
        [conversationId]: [...newMessages],
      };

      localStorage.setItem(
        MESSAGES_STORAGE_KEY,
        JSON.stringify(updated)
      );

      return updated;
    });
  };

  const deleteMessages = (
    conversationId
  ) => {
    setSavedMessages((current) => {
      const updated = {
        ...current,
      };

      delete updated[conversationId];

      localStorage.setItem(
        MESSAGES_STORAGE_KEY,
        JSON.stringify(updated)
      );

      return updated;
    });
  };

  const sendMessage = async (
    content,
    projectId = "devmind-ai",
    conversationId,
    sessionId = null
  ) => {
    const trimmedContent =
      content.trim();

    if (
      !trimmedContent ||
      isProcessing ||
      !conversationId
    ) {
      return null;
    }

    setChatError(null);
    setFailedMessage(null);

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedContent,
    };

    const optimisticMessages = [
      ...messages,
      userMessage,
    ];

    setMessages(optimisticMessages);

    saveMessages(
      conversationId,
      optimisticMessages
    );

    setIsProcessing(true);

    try {
      const result =
        await sendChatMessage(
          sessionId,
          trimmedContent
        );

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: result.response,
      };

      const updatedMessages = [
        ...optimisticMessages,
        assistantMessage,
      ];

      setMessages(updatedMessages);

      saveMessages(
        conversationId,
        updatedMessages
      );

      setFailedMessage(null);

      return {
        sessionId: result.session_id,
      };
    } catch (error) {
      console.error(
        "Failed to send chat message:",
        error
      );

      setFailedMessage({
        content: trimmedContent,
        projectId,
        conversationId,
        sessionId,
      });

      setChatError(
        "Unable to connect to DevMind. Make sure the backend is running."
      );

      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  const retryMessage = async () => {
    if (!failedMessage || isProcessing) {
      return null;
    }

    const {
      content,
      conversationId,
      sessionId,
    } = failedMessage;

    setChatError(null);
    setIsProcessing(true);

    try {
      const result =
        await sendChatMessage(
          sessionId,
          content
        );

      const assistantMessage = {
        id: Date.now(),
        role: "assistant",
        content: result.response,
      };

      const updatedMessages = [
        ...messages,
        assistantMessage,
      ];

      setMessages(updatedMessages);

      saveMessages(
        conversationId,
        updatedMessages
      );

      setFailedMessage(null);
      setChatError(null);

      return {
        sessionId: result.session_id,
      };
    } catch (error) {
      console.error(
        "Retry failed:",
        error
      );

      setChatError(
        "Unable to connect to DevMind. Make sure the backend is running."
      );

      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  const clearChatError = () => {
    setChatError(null);
  };

  return {
    messages,
    isProcessing,
    chatError,
    retryMessage,
    sendMessage,
    clearMessages,
    loadMessages,
    deleteMessages,
    clearChatError,
  };
}

export default useChat;