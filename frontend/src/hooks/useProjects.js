import { useCallback, useEffect, useState } from "react";

import {
  getProjects,
  createProject as createProjectRequest,
  disconnectProject as disconnectProjectRequest,
  reconnectProject as reconnectProjectRequest,
  removeProject as removeProjectRequest,
  importProjectFromFolder as importProjectFromFolderRequest,
} from "../api/client";

/* Owns the project list and the active project. */
function useProjects() {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [isProjectsLoading, setIsProjectsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadProjects = async () => {
      try {
        const loadedProjects = await getProjects();
        if (cancelled) return;

        const safeProjects = Array.isArray(loadedProjects)
          ? loadedProjects
          : [];
        setProjects(safeProjects);
        setActiveProject((current) => {
          if (current) {
            const freshCurrent = safeProjects.find(
              (project) => project.id === current.id
            );
            if (freshCurrent) return freshCurrent;
          }
          return safeProjects[0] || null;
        });
      } catch (error) {
        if (!cancelled) {
          console.error("Failed to load projects:", error);
          setProjects([]);
          setActiveProject(null);
        }
      } finally {
        if (!cancelled) setIsProjectsLoading(false);
      }
    };

    loadProjects();
    return () => {
      cancelled = true;
    };
  }, []);

  const patchProject = useCallback((projectId, patch) => {
    setProjects((current) =>
      current.map((project) =>
        project.id === projectId ? { ...project, ...patch } : project
      )
    );
    setActiveProject((current) =>
      current?.id === projectId ? { ...current, ...patch } : current
    );
  }, []);

  const refreshProjects = useCallback(async () => {
    const loadedProjects = await getProjects();
    const safeProjects = Array.isArray(loadedProjects) ? loadedProjects : [];
    setProjects(safeProjects);
    setActiveProject((current) => {
      if (!current) return safeProjects[0] || null;
      return safeProjects.find((project) => project.id === current.id) ||
        safeProjects[0] || null;
    });
    return safeProjects;
  }, []);

  const createProject = async (name, repositoryPath) => {
    const project = await createProjectRequest(name, repositoryPath);
    setProjects((current) => [
      ...current.filter((item) => item.id !== project.id),
      project,
    ]);
    setActiveProject(project);
    return project;
  };

  const importProjectFromFolder = async (name, selectedFiles, onProgress) => {
    const result = await importProjectFromFolderRequest(name, selectedFiles, onProgress);
    const project = result?.project;

    if (!project?.id) {
      throw new Error("Folder import completed without a valid project response.");
    }

    setProjects((current) => [
      ...current.filter((item) => item.id !== project.id),
      project,
    ]);
    setActiveProject(project);
    return result;
  };

  const disconnectProject = async (projectId) => {
    if (!projectId) return null;
    const updatedProject = await disconnectProjectRequest(projectId);
    patchProject(projectId, { ...(updatedProject || {}), connected: false });
    return updatedProject;
  };

  const reconnectProject = async (projectId) => {
    if (!projectId) return null;
    const updatedProject = await reconnectProjectRequest(projectId);
    patchProject(projectId, { ...(updatedProject || {}), connected: true });
    return updatedProject;
  };

  const removeProject = async (projectId) => {
    if (!projectId) return null;
    await removeProjectRequest(projectId);

    const wasActive = activeProject?.id === projectId;
    const remainingProjects = projects.filter(
      (project) => project.id !== projectId
    );
    setProjects(remainingProjects);
    if (wasActive) setActiveProject(remainingProjects[0] || null);

    return { wasActive };
  };

  return {
    projects,
    activeProject,
    setActiveProject,
    isProjectsLoading,
    patchProject,
    refreshProjects,
    createProject,
    importProjectFromFolder,
    disconnectProject,
    reconnectProject,
    removeProject,
  };
}

export default useProjects;
