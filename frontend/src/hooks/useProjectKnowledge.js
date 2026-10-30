import { useCallback, useEffect, useRef, useState } from "react";

import {
  getProjectKnowledgeStats,
  getProjectChanges,
  uploadFiles as uploadFileRequest,
  updateProjectKnowledge as updateProjectKnowledgeRequest,
} from "../api/client";

/* Owns project knowledge statistics, change detection, indexing and uploads. */
function useProjectKnowledge({ activeProject, patchProject, refreshProjects }) {
  const [isUploading, setIsUploading] = useState(false);
  const [isUpdatingKnowledge, setIsUpdatingKnowledge] = useState(false);
  const [knowledgeUpdateError, setKnowledgeUpdateError] = useState(null);
  const [knowledgeUpdateResult, setKnowledgeUpdateResult] = useState(null);
  const [projectChanges, setProjectChanges] = useState(null);
  const [isCheckingChanges, setIsCheckingChanges] = useState(false);
  const [changeDetectionError, setChangeDetectionError] = useState(null);

  const activeProjectIdRef = useRef(activeProject?.id ?? null);
  const changesRequestIdRef = useRef(0);
  const updateRequestIdRef = useRef(0);
  const uploadRequestIdRef = useRef(0);
  activeProjectIdRef.current = activeProject?.id ?? null;

  const clearProjectChanges = useCallback(() => {
    changesRequestIdRef.current += 1;
    setProjectChanges(null);
    setChangeDetectionError(null);
    setIsCheckingChanges(false);
  }, []);

  const resetKnowledgeState = useCallback(() => {
    clearProjectChanges();
    updateRequestIdRef.current += 1;
    setKnowledgeUpdateError(null);
    setKnowledgeUpdateResult(null);
    setIsUpdatingKnowledge(false);
  }, [clearProjectChanges]);

  const loadProjectKnowledgeStats = useCallback(async (projectId) => {
    if (!projectId) return null;
    try {
      const stats = await getProjectKnowledgeStats(projectId);
      // Stats belong to the requested project, so safely patch that project
      // even if the user switched projects while the request was in flight.
      patchProject(projectId, {
        indexed_files: stats?.indexed_files ?? 0,
        chunks: stats?.chunks ?? 0,
      });
      return stats;
    } catch (error) {
      console.error("Failed to load project knowledge statistics:", error);
      return null;
    }
  }, [patchProject]);

  const loadProjectChanges = useCallback(async (projectId) => {
    if (!projectId) {
      if (!activeProjectIdRef.current) clearProjectChanges();
      return null;
    }

    const requestId = ++changesRequestIdRef.current;
    const isCurrentProject = () =>
      activeProjectIdRef.current === projectId &&
      changesRequestIdRef.current === requestId;

    if (activeProjectIdRef.current === projectId) {
      setIsCheckingChanges(true);
      setChangeDetectionError(null);
    }

    try {
      const changes = await getProjectChanges(projectId);
      if (isCurrentProject()) {
        setProjectChanges(changes);
        setChangeDetectionError(null);
      }
      return changes;
    } catch (error) {
      console.error("Failed to check project changes:", error);
      if (isCurrentProject()) {
        setChangeDetectionError(
          error?.message || "Couldn't check project changes."
        );
      }
      return null;
    } finally {
      if (isCurrentProject()) setIsCheckingChanges(false);
    }
  }, [clearProjectChanges]);

  const updateProjectKnowledge = async (projectId) => {
    if (!projectId) return null;
    if (activeProject?.id !== projectId || !activeProject?.connected) {
      throw new Error("This project is disconnected or is no longer active.");
    }

    const requestId = ++updateRequestIdRef.current;
    const isCurrentRequest = () =>
      updateRequestIdRef.current === requestId &&
      activeProjectIdRef.current === projectId;

    setIsUpdatingKnowledge(true);
    setKnowledgeUpdateError(null);
    setKnowledgeUpdateResult(null);

    try {
      const result = await updateProjectKnowledgeRequest(projectId);
      if (isCurrentRequest()) setKnowledgeUpdateResult(result);
      await Promise.all([
        loadProjectKnowledgeStats(projectId),
        loadProjectChanges(projectId),
      ]);
      return result;
    } catch (error) {
      console.error("Failed to update project knowledge:", error);
      if (isCurrentRequest()) {
        setKnowledgeUpdateError(
          error?.message || "Couldn't update project knowledge."
        );
      }
      await loadProjectChanges(projectId);
      throw error;
    } finally {
      if (isCurrentRequest()) setIsUpdatingKnowledge(false);
    }
  };

  const uploadFiles = async (files) => {
    const project = activeProject;
    if (!project) {
      throw new Error("Please select a project before uploading files.");
    }
    if (!project.connected) throw new Error("This project is disconnected.");

    const requestId = ++uploadRequestIdRef.current;
    setIsUploading(true);
    try {
      const result = await uploadFileRequest(project.id, files);
      try {
        await refreshProjects();
      } catch (error) {
        console.error("Files uploaded, but failed to refresh projects:", error);
      }
      await Promise.all([
        loadProjectKnowledgeStats(project.id),
        loadProjectChanges(project.id),
      ]);
      return result;
    } finally {
      if (uploadRequestIdRef.current === requestId) setIsUploading(false);
    }
  };

  useEffect(() => {
    const projectId = activeProject?.id;
    if (!projectId) {
      clearProjectChanges();
      setKnowledgeUpdateError(null);
      setKnowledgeUpdateResult(null);
      setIsUpdatingKnowledge(false);
      return;
    }

    void loadProjectKnowledgeStats(projectId);
    void loadProjectChanges(projectId);
  }, [activeProject?.id, clearProjectChanges, loadProjectChanges, loadProjectKnowledgeStats]);

  return {
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
    clearProjectChanges,
    resetKnowledgeState,
  };
}

export default useProjectKnowledge;
