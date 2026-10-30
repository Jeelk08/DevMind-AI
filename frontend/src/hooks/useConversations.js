import { useEffect, useRef, useState } from "react";

import {
  loadConversations,
  saveConversations,
  loadActiveConversationId,
  saveActiveConversationId
} from "./devmindStorage";

/* Owns conversation state, persistence, restoration and message sending. */
function useConversations({
  chat,
  context,
  projects,
  activeProject,
  setActiveProject,
  isProjectsLoading,
}) {
  const [conversations, setConversations] = useState(loadConversations);
  const [activeConversationId, setActiveConversationId] = useState(
    loadActiveConversationId
  );
  const [isConversationLoading, setIsConversationLoading] = useState(false);
  const [conversationError, setConversationError] = useState(null);
  const initialRestoreAttempted = useRef(false);

  const isProcessing = chat.isProcessing || context.state === "loading";

  useEffect(() => {
    saveConversations(conversations);
  }, [conversations]);

  useEffect(() => {
    saveActiveConversationId(activeConversationId);
  }, [activeConversationId]);

  const restoreConversation = async (conversation) => {
    if (!conversation) {
      setActiveConversationId(null);
      return;
    }

    setIsConversationLoading(true);
    setConversationError(null);

    try {
      const project =
        projects.find((item) => item.id === conversation.projectId) ||
        projects[0] ||
        null;

      if (!project) {
        setActiveProject(null);
        chat.clearMessages();
        context.clearContext();
        setActiveConversationId(null);
        setConversationError(
          "The project for this conversation is unavailable. Please select a project."
        );
        return;
      }

      setActiveProject(project);
      chat.loadMessages(conversation.id);

      if (conversation.contextQuery) {
        await context.retrieveContext(conversation.contextQuery, project.id);
      } else {
        context.clearContext();
      }
    } catch (error) {
      console.error("Failed to restore conversation:", error);
      setConversationError("Couldn't load this conversation.");
    } finally {
      setIsConversationLoading(false);
    }
  };

  /* Wait for the initial project request before restoring saved state. */
  useEffect(() => {
    if (isProjectsLoading || initialRestoreAttempted.current) return;
    initialRestoreAttempted.current = true;

    if (!activeConversationId) return;

    const savedConversation = conversations.find(
      (item) => item.id === activeConversationId
    );

    if (!savedConversation) {
      setActiveConversationId(null);
      return;
    }

    void restoreConversation(savedConversation);
    // Initial restoration should happen once, after projects have loaded.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isProjectsLoading]);

  const sendMessage = async (content) => {
    const trimmedContent = content.trim();

    if (!activeProject) {
      setConversationError("Please select a project first.");
      return;
    }

    if (!trimmedContent || isProcessing || isConversationLoading) return;

    let conversationId = activeConversationId;

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
      setConversations((current) => [newConversation, ...current]);
      setActiveConversationId(conversationId);
    } else {
      setConversations((current) => {
        const conversation = current.find(
          (item) => item.id === conversationId
        );
        if (!conversation) return current;
        const updatedConversation = {
          ...conversation,
          updatedAt: "Just now",
          contextQuery: trimmedContent,
        };
        return [
          updatedConversation,
          ...current.filter((item) => item.id !== conversationId),
        ];
      });
    }

    setConversationError(null);
    chat.clearChatError();

    const existingConversation = conversations.find(
      (item) => item.id === conversationId
    );
    const backendSessionId = existingConversation?.backendSessionId || null;

    try {
      const [, chatResult] = await Promise.all([
        context.retrieveContext(trimmedContent, activeProject.id),
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
              ? { ...item, backendSessionId: chatResult.sessionId }
              : item
          )
        );
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  const newChat = () => {
    chat.clearMessages();
    context.clearContext();
    setConversationError(null);
    setActiveConversationId(null);
  };

  const deleteConversation = (conversationId) => {
    setConversations((current) =>
      current.filter((conversation) => conversation.id !== conversationId)
    );
    chat.deleteMessages(conversationId);
    if (activeConversationId === conversationId) newChat();
  };

  const renameConversation = (conversationId, newTitle) => {
    const trimmedTitle = newTitle.trim();
    if (!trimmedTitle) return;
    setConversations((current) =>
      current.map((conversation) =>
        conversation.id === conversationId
          ? { ...conversation, title: trimmedTitle }
          : conversation
      )
    );
  };

  const selectConversation = async (conversationId) => {
    const conversation = conversations.find(
      (item) => item.id === conversationId
    );
    if (!conversation) return;
    setActiveConversationId(conversationId);
    await restoreConversation(conversation);
  };

  const retryConversation = async () => {
    if (!activeConversationId) return;
    const conversation = conversations.find(
      (item) => item.id === activeConversationId
    );
    if (!conversation) {
      setActiveConversationId(null);
      return;
    }
    await restoreConversation(conversation);
  };

  const createConversation = () => {
    if (!activeProject) {
      setConversationError("Please select a project first.");
      return;
    }
    const conversation = {
      id: `conv-${Date.now()}`,
      title: "New conversation",
      projectId: activeProject.id,
      updatedAt: "Just now",
      backendSessionId: null,
    };
    setConversations((current) => [conversation, ...current]);
    setActiveConversationId(conversation.id);
    setConversationError(null);
    chat.clearMessages();
    context.clearContext();
  };

  return {
    conversations,
    activeConversationId,
    isConversationLoading,
    conversationError,
    isProcessing,
    selectConversation,
    createConversation,
    deleteConversation,
    renameConversation,
    retryConversation,
    newChat,
    sendMessage,
  };
}

export default useConversations;