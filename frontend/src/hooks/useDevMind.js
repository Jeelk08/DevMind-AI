import useChat from "./useChat";
import useContext from "./useContext";

import useProjects from "./useProjects";
import useProjectKnowledge from "./useProjectKnowledge";
import useConversations from "./useConversations";

/*
 * Composes the DevMind hooks and coordinates the
 * state resets that span more than one of them.
 *
 * - useProjects         project list + active project
 * - useProjectKnowledge stats, change detection, indexing, uploads
 * - useConversations    conversations, persistence, sending messages
 */
function useDevMind() {
  const chat = useChat();
  const context = useContext();

  const projectsApi = useProjects();

  const {
    projects,
    activeProject,
    setActiveProject,
    isProjectsLoading,
    patchProject,
    refreshProjects,
  } = projectsApi;

  const knowledge = useProjectKnowledge({
    activeProject,
    patchProject,
    refreshProjects,
  });

  const conversationsApi = useConversations({
    chat,
    context,
    projects,
    activeProject,
    setActiveProject,
    isProjectsLoading,
  });

  /*
   * Clear everything tied to the current project:
   * conversation, messages, context and knowledge state.
   */
  const resetProjectScopedState = () => {
    conversationsApi.newChat();
    knowledge.resetKnowledgeState();
  };

  const switchProject = (project) => {
    setActiveProject(project);
    resetProjectScopedState();
  };

  const importProjectFromFolder = async (name, selectedFiles, onProgress) => {
    const result = await projectsApi.importProjectFromFolder(name, selectedFiles, onProgress);
    resetProjectScopedState();
    return result;
  };

  const createProject = async (name, repositoryPath) => {
    const project = await projectsApi.createProject(
      name,
      repositoryPath
    );

    resetProjectScopedState();

    return project;
  };

  const disconnectProject = async (projectId) => {
    const updatedProject =
      await projectsApi.disconnectProject(projectId);

    knowledge.clearProjectChanges();

    return updatedProject;
  };

  /*
   * Reconnected projects should immediately have
   * their current change state checked.
   */
  const reconnectProject = async (projectId) => {
    const updatedProject =
      await projectsApi.reconnectProject(projectId);

    if (projectId) {
      await knowledge.loadProjectChanges(projectId);
    }

    return updatedProject;
  };

  const removeProject = async (projectId) => {
    const result = await projectsApi.removeProject(projectId);

    if (!result) {
      return null;
    }

    if (result.wasActive) {
      resetProjectScopedState();
    }

    return true;
  };

  return {
    projects,
    activeProject,

    switchProject,
    createProject,
    importProjectFromFolder,

    disconnectProject,
    reconnectProject,
    removeProject,

    uploadFiles: knowledge.uploadFiles,
    isUploading: knowledge.isUploading,

    updateProjectKnowledge: knowledge.updateProjectKnowledge,
    isUpdatingKnowledge: knowledge.isUpdatingKnowledge,
    knowledgeUpdateError: knowledge.knowledgeUpdateError,
    knowledgeUpdateResult: knowledge.knowledgeUpdateResult,

    projectChanges: knowledge.projectChanges,
    isCheckingChanges: knowledge.isCheckingChanges,
    changeDetectionError: knowledge.changeDetectionError,
    loadProjectChanges: knowledge.loadProjectChanges,

    conversations: conversationsApi.conversations,
    activeConversationId: conversationsApi.activeConversationId,
    selectConversation: conversationsApi.selectConversation,
    createConversation: conversationsApi.createConversation,
    deleteConversation: conversationsApi.deleteConversation,
    renameConversation: conversationsApi.renameConversation,

    newChat: conversationsApi.newChat,

    messages: chat.messages,
    isProcessing: conversationsApi.isProcessing,
    isConversationLoading: conversationsApi.isConversationLoading,

    conversationError: conversationsApi.conversationError,

    chatError: chat.chatError,
    clearChatError: chat.clearChatError,
    retryMessage: chat.retryMessage,

    retryConversation: conversationsApi.retryConversation,

    contextState: context.state,
    contextSources: context.sources,
    contextQuery: context.query,

    sendMessage: conversationsApi.sendMessage,
  };
}

export default useDevMind;