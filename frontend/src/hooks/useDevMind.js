import { useEffect, useState } from "react";

import useChat from "./useChat";
import useContext from "./useContext";
import {
  getProjects,
  createProject as createProjectRequest,
} from "../api/client";



const initialConversations = [];

const CONVERSATIONS_STORAGE_KEY =
  "devmind-conversations";

const ACTIVE_CONVERSATION_STORAGE_KEY =
  "devmind-active-conversation";

function useDevMind() {
  const chat = useChat();
  const context = useContext();

  const [projects, setProjects] =
    useState([]);

  const [activeProject, setActiveProject] =
    useState(null);

  const [conversations, setConversations] =
    useState(() => {
      const saved = localStorage.getItem(
        CONVERSATIONS_STORAGE_KEY
      );

      if (!saved) {
        return initialConversations;
      }

      try {
        return JSON.parse(saved);
      } catch {
        return initialConversations;
      }
    });

  const [activeConversationId, setActiveConversationId] =
    useState(() => {
      return localStorage.getItem(
        ACTIVE_CONVERSATION_STORAGE_KEY
      );
    });

  const [isConversationLoading, setIsConversationLoading] =
    useState(false);

  const [conversationError, setConversationError] =
    useState(null);

  useEffect(() => {
    localStorage.setItem(
      CONVERSATIONS_STORAGE_KEY,
      JSON.stringify(conversations)
    );
  }, [conversations]);

  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem(
        ACTIVE_CONVERSATION_STORAGE_KEY,
        activeConversationId
      );
    } else {
      localStorage.removeItem(
        ACTIVE_CONVERSATION_STORAGE_KEY
      );
    }
  }, [activeConversationId]);

  const restoreConversation = async (
    conversation
  ) => {
    if (!conversation) {
      setActiveConversationId(null);
      return;
    }

    setIsConversationLoading(true);
    setConversationError(null);

    try {
      const project =
        projects.find(
          (item) =>
            item.id === conversation.projectId
        ) || projects[0];

      setActiveProject(project);

      chat.loadMessages(conversation.id);

      if (conversation.contextQuery) {
        await context.retrieveContext(
          conversation.contextQuery,
          conversation.projectId
        );
      } else {
        context.clearContext();
      }

      setIsConversationLoading(false);
    } catch (error) {
      console.error(
        "Failed to restore conversation:",
        error
      );

      setConversationError(
        "Couldn't load this conversation."
      );

      setIsConversationLoading(false);
    }
  };

  useEffect(() => {
    if (!activeConversationId) {
      return;
    }

    const savedConversation =
      conversations.find(
        (item) =>
          item.id === activeConversationId
      );

    if (!savedConversation) {
      setActiveConversationId(null);
      return;
    }

    restoreConversation(savedConversation);
  }, []);

  const sendMessage = async (content) => {
    const trimmedContent = content.trim();

    if (!activeProject) {
      setConversationError(
        "Please select a project first."
      );
      return;
    }

    if (
      !trimmedContent ||
      isProcessing ||
      isConversationLoading
    ) {
      return;
    }

    let conversationId =
      activeConversationId;

    if (!conversationId) {
      conversationId = `conv-${Date.now()}`;

      const newConversation = {
        id: conversationId,
        title:
          trimmedContent.length > 30
            ? `${trimmedContent.slice(0, 30)}...`
            : trimmedContent,
        projectId: activeProject.id,
        updatedAt: "Just now",
        contextQuery: trimmedContent,
        backendSessionId: null,
      };

      setConversations((current) => [
        newConversation,
        ...current,
      ]);

      setActiveConversationId(
        conversationId
      );
    } else {
      setConversations((current) => {
        const conversation =
          current.find(
            (item) =>
              item.id === conversationId
          );

        if (!conversation) {
          return current;
        }

        const updatedConversation = {
          ...conversation,
          updatedAt: "Just now",
          contextQuery: trimmedContent,
        };

        return [
          updatedConversation,
          ...current.filter(
            (item) =>
              item.id !== conversationId
          ),
        ];
      });
    }

    setConversationError(null);
    chat.clearChatError();

    const existingConversation =
      conversations.find(
        (item) =>
          item.id === conversationId
      );

    const backendSessionId =
      existingConversation?.backendSessionId || null;

    try {
      const [, chatResult] =
        await Promise.all([
          context.retrieveContext(
            trimmedContent,
            activeProject.id
          ),

          chat.sendMessage(
            trimmedContent,
            activeProject.id,
            conversationId,
            backendSessionId
          ),
        ]);

      if (chatResult?.sessionId) {
        setConversations((current) =>
          current.map((item) =>
            item.id === conversationId
              ? {
                  ...item,
                  backendSessionId:
                    chatResult.sessionId,
                }
              : item
          )
        );
      }
    } catch (error) {
      console.error(
        "Failed to send message:",
        error
      );
    }
  };

  const switchProject = (project) => {
    setActiveProject(project);
    context.clearContext();
  };



  const createProject = async (
    name,
    repositoryPath
  ) => {
    const project = await createProjectRequest(
      name,
      repositoryPath
    );

    setProjects((current) => [
      ...current,
      project,
    ]);

    setActiveProject(project);

    context.clearContext();

    return project;
  };


  const newChat = () => {
    chat.clearMessages();
    context.clearContext();
    setConversationError(null);
    setActiveConversationId(null);
  };

  const deleteConversation = (
    conversationId
  ) => {
    setConversations((current) =>
      current.filter(
        (conversation) =>
          conversation.id !== conversationId
      )
    );

    chat.deleteMessages(conversationId);

    if (
      activeConversationId ===
      conversationId
    ) {
      chat.clearMessages();
      context.clearContext();
      setConversationError(null);
      setActiveConversationId(null);
    }
  };

  const renameConversation = (
    conversationId,
    newTitle
  ) => {
    const trimmedTitle =
      newTitle.trim();

    if (!trimmedTitle) {
      return;
    }

    setConversations((current) =>
      current.map((conversation) =>
        conversation.id ===
        conversationId
          ? {
              ...conversation,
              title: trimmedTitle,
            }
          : conversation
      )
    );
  };

  const selectConversation = async (
    conversationId
  ) => {
    const conversation =
      conversations.find(
        (item) =>
          item.id === conversationId
      );

    if (!conversation) {
      return;
    }

    setActiveConversationId(
      conversationId
    );

    await restoreConversation(
      conversation
    );
  };

  const retryConversation = async () => {
    if (!activeConversationId) {
      return;
    }

    const conversation =
      conversations.find(
        (item) =>
          item.id === activeConversationId
      );

    if (!conversation) {
      setActiveConversationId(null);
      return;
    }

    await restoreConversation(
      conversation
    );
  };

  const createConversation = () => {
    if (!activeProject) {
      setConversationError(
        "Please select a project first."
      );
      return;
    }
    const conversation = {
      id: `conv-${Date.now()}`,
      title: "New conversation",
      projectId: activeProject.id,
      updatedAt: "Just now",
      backendSessionId: null,
    };

    setConversations((current) => [
      conversation,
      ...current,
    ]);

    setActiveConversationId(
      conversation.id
    );

    setConversationError(null);

    chat.clearMessages();
    context.clearContext();
  };


  const isProcessing =
    chat.isProcessing ||
    context.state === "loading";
  
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const loadedProjects =
          await getProjects();

        setProjects(loadedProjects);

        if (loadedProjects.length > 0) {
          setActiveProject(
            loadedProjects[0]
          );
        }
      } catch (error) {
        console.error(
          "Failed to load projects:",
          error
        );
      }
    };

    loadProjects();
  }, []);

  return {
    projects,
    activeProject,
    switchProject,
    createProject,

    conversations,
    activeConversationId,
    selectConversation,
    createConversation,
    deleteConversation,
    renameConversation,

    newChat,

    messages: chat.messages,
    isProcessing,
    isConversationLoading,

    conversationError,

    // NEW
    chatError: chat.chatError,
    clearChatError: chat.clearChatError,
    retryMessage: chat.retryMessage,

    retryConversation,

    contextState: context.state,
    contextSources: context.sources,
    contextQuery: context.query,
    

    sendMessage,
  };
}

export default useDevMind;