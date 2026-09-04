import { useEffect, useState } from "react";

import useChat from "./useChat";
import useContext from "./useContext";

import {
  getProjects,
  getProjectKnowledgeStats,
  getProjectChanges,
  createProject as createProjectRequest,
  disconnectProject as disconnectProjectRequest,
  reconnectProject as reconnectProjectRequest,
  removeProject as removeProjectRequest,
  uploadFiles as uploadFileRequest,
  updateProjectKnowledge as updateProjectKnowledgeRequest,
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

  const [isUploading, setIsUploading] =
    useState(false);

  const [isUpdatingKnowledge, setIsUpdatingKnowledge] =
    useState(false);

  const [knowledgeUpdateError, setKnowledgeUpdateError] =
    useState(null);

  const [knowledgeUpdateResult, setKnowledgeUpdateResult] =
    useState(null);

  const [projectChanges, setProjectChanges] =
    useState(null);

  const [isCheckingChanges, setIsCheckingChanges] =
    useState(false);

  const [changeDetectionError, setChangeDetectionError] =
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
      existingConversation?.backendSessionId ||
      null;

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

    setActiveConversationId(null);
    chat.clearMessages();
    context.clearContext();
    setConversationError(null);

    setProjectChanges(null);
    setChangeDetectionError(null);
    setKnowledgeUpdateError(null);
    setKnowledgeUpdateResult(null);
  };

  const createProject = async (
    name,
    repositoryPath
  ) => {
    const project =
      await createProjectRequest(
        name,
        repositoryPath
      );

    setProjects((current) => [
      ...current,
      project,
    ]);

    setActiveProject(project);
    setActiveConversationId(null);
    chat.clearMessages();
    context.clearContext();
    setConversationError(null);

    setProjectChanges(null);
    setChangeDetectionError(null);
    setKnowledgeUpdateError(null);
    setKnowledgeUpdateResult(null);

    return project;
  };

  /*
   * Disconnect the active project.
   *
   * The project remains in the project list and
   * its existing knowledge is preserved.
   */
  const disconnectProject = async (
    projectId
  ) => {
    if (!projectId) {
      return null;
    }

    const updatedProject =
      await disconnectProjectRequest(
        projectId
      );

    setProjects((current) =>
      current.map((project) =>
        project.id === projectId
          ? {
              ...project,
              ...(updatedProject || {}),
              connected: false,
            }
          : project
      )
    );

    setActiveProject((current) => {
      if (
        !current ||
        current.id !== projectId
      ) {
        return current;
      }

      return {
        ...current,
        ...(updatedProject || {}),
        connected: false,
      };
    });

    setProjectChanges(null);
    setChangeDetectionError(null);

    return updatedProject;
  };

  /*
   * Reconnect the project.
   *
   * Existing conversations and project knowledge
   * remain untouched.
   */
  const reconnectProject = async (
    projectId
  ) => {
    if (!projectId) {
      return null;
    }

    const updatedProject =
      await reconnectProjectRequest(
        projectId
      );

    setProjects((current) =>
      current.map((project) =>
        project.id === projectId
          ? {
              ...project,
              ...(updatedProject || {}),
              connected: true,
            }
          : project
      )
    );

    setActiveProject((current) => {
      if (
        !current ||
        current.id !== projectId
      ) {
        return current;
      }

      return {
        ...current,
        ...(updatedProject || {}),
        connected: true,
      };
    });

    /*
     * Reconnected projects should immediately
     * have their current change state checked.
     */
    await loadProjectChanges(projectId);

    return updatedProject;
  };

  /*
   * Remove the project from DevMind.
   *
   * This removes the project from the DevMind
   * project list and clears its active UI state.
   * The repository files on disk are not deleted.
   */
  const removeProject = async (
    projectId
  ) => {
    if (!projectId) {
      return null;
    }

    await removeProjectRequest(projectId);

    const remainingProjects =
      projects.filter(
        (project) => project.id !== projectId
      );

    setProjects(remainingProjects);

    if (activeProject?.id === projectId) {
      const nextProject =
        remainingProjects[0] || null;

      setActiveProject(nextProject);
      setActiveConversationId(null);
      chat.clearMessages();
      context.clearContext();
      setConversationError(null);

      setProjectChanges(null);
      setChangeDetectionError(null);
      setKnowledgeUpdateError(null);
      setKnowledgeUpdateResult(null);
    }

    return true;
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

  /*
   * Load knowledge statistics for a project.
   *
   * The backend reads the existing persistent
   * repository index and returns:
   *
   * {
   *   indexed_files: number,
   *   chunks: number
   * }
   *
   * This does NOT trigger a re-index.
   */
  const loadProjectKnowledgeStats = async (
    projectId
  ) => {
    if (!projectId) {
      return;
    }

    try {
      const stats =
        await getProjectKnowledgeStats(
          projectId
        );

      const indexedFiles =
        stats?.indexed_files ?? 0;

      const chunks =
        stats?.chunks ?? 0;

      setProjects((currentProjects) =>
        currentProjects.map((project) =>
          project.id === projectId
            ? {
                ...project,
                indexed_files: indexedFiles,
                chunks: chunks,
              }
            : project
        )
      );

      setActiveProject((currentProject) =>
        currentProject?.id === projectId
          ? {
              ...currentProject,
              indexed_files: indexedFiles,
              chunks: chunks,
            }
          : currentProject
      );
    } catch (error) {
      console.error(
        "Failed to load project knowledge statistics:",
        error
      );
    }
  };

  /*
   * Load the current filesystem changes for
   * the active project.
   *
   * This only detects changes.
   * It does NOT trigger indexing.
   */
  const loadProjectChanges = async (
    projectId
  ) => {
    if (!projectId) {
      setProjectChanges(null);
      return null;
    }

    setIsCheckingChanges(true);
    setChangeDetectionError(null);

    try {
      const changes =
        await getProjectChanges(
          projectId
        );

      setProjectChanges(changes);

      return changes;
    } catch (error) {
      console.error(
        "Failed to check project changes:",
        error
      );

      setChangeDetectionError(
        error?.message ||
          "Couldn't check project changes."
      );

      return null;
    } finally {
      setIsCheckingChanges(false);
    }
  };

  /*
   * Update project knowledge using the backend's
   * incremental indexing pipeline.
   */
  const updateProjectKnowledge = async (
    projectId
  ) => {
    if (!projectId) {
      return null;
    }

    if (!activeProject?.connected) {
      throw new Error(
        "This project is disconnected."
      );
    }

    setIsUpdatingKnowledge(true);
    setKnowledgeUpdateError(null);
    setKnowledgeUpdateResult(null);

    try {
      const result =
        await updateProjectKnowledgeRequest(
          projectId
        );

      setKnowledgeUpdateResult(result);

      /*
       * Refresh the displayed knowledge
       * statistics after indexing.
       */
      await loadProjectKnowledgeStats(
        projectId
      );

      /*
       * Re-check filesystem changes.
       *
       * This is important because a successful
       * index should clear the "changes available"
       * state when everything was processed.
       */
      await loadProjectChanges(
        projectId
      );

      return result;
    } catch (error) {
      console.error(
        "Failed to update project knowledge:",
        error
      );

      setKnowledgeUpdateError(
        error?.message ||
          "Couldn't update project knowledge."
      );

      /*
       * Also refresh change detection after
       * a failed update so the UI reflects the
       * actual current filesystem state.
       */
      await loadProjectChanges(
        projectId
      );

      throw error;
    } finally {
      setIsUpdatingKnowledge(false);
    }
  };

  /*
   * Load projects when the application starts.
   */
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

  /*
   * Whenever the active project changes,
   * load its current knowledge statistics
   * and filesystem change state.
   *
   * This handles:
   * - Initial project selection
   * - Project switching
   * - Conversation restoration
   * - Newly created projects
   */
  useEffect(() => {
    if (!activeProject?.id) {
      setProjectChanges(null);
      return;
    }

    loadProjectKnowledgeStats(
      activeProject.id
    );

    loadProjectChanges(
      activeProject.id
    );
  }, [activeProject?.id]);

  const uploadFiles = async (files) => {
    if (!activeProject) {
      throw new Error(
        "Please select a project before uploading files."
      );
    }

    if (!activeProject.connected) {
      throw new Error(
        "This project is disconnected."
      );
    }

    setIsUploading(true);

    try {
      const result =
        await uploadFileRequest(
          activeProject.id,
          files
        );

      /*
       * Refresh project data first.
       */
      try {
        const loadedProjects =
          await getProjects();

        setProjects(loadedProjects);

        const updatedActiveProject =
          loadedProjects.find(
            (project) =>
              project.id === activeProject.id
          );

        if (updatedActiveProject) {
          setActiveProject(
            updatedActiveProject
          );
        }
      } catch (error) {
        console.error(
          "Files uploaded, but failed to refresh projects:",
          error
        );
      }

      /*
       * Explicitly refresh knowledge statistics
       * after upload so the card immediately shows
       * the new indexed file/chunk counts.
       */
      await loadProjectKnowledgeStats(
        activeProject.id
      );

      /*
       * Also refresh change detection so the
       * Recent Changes state stays accurate.
       */
      await loadProjectChanges(
        activeProject.id
      );

      return result;
    } finally {
      setIsUploading(false);
    }
  };

  return {
    projects,
    activeProject,

    switchProject,
    createProject,

    disconnectProject,
    reconnectProject,
    removeProject,

    uploadFiles,
    isUploading,

    updateProjectKnowledge,
    isUpdatingKnowledge,
    knowledgeUpdateError,
    knowledgeUpdateResult,

    projectChanges,
    isCheckingChanges,
    changeDetectionError,
    loadProjectChanges,

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