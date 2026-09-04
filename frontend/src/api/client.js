const API_BASE_URL = "http://127.0.0.1:8000";

export async function sendChatMessage(
  sessionId,
  message,
  projectId
) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/chat`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          project_id: projectId,
        }),
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "DevMind returned an error.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid response."
    );
  }
}

export async function retrieveContext(
  query,
  projectId
) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/context`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          project_id: projectId,
        }),
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "DevMind returned a context error.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid context response."
    );
  }
}

export async function getProjects() {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects`
    );
  } catch {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    throw new Error(
      "Failed to load projects."
    );
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid project response."
    );
  }
}


export async function getProjectKnowledgeStats(
  projectId
) {
  if (!projectId) {
    throw new Error(
      "A project must be selected."
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}/stats`
    );
  } catch {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to load project knowledge statistics.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid statistics response."
    );
  }
}




export async function createProject(
  name,
  repositoryPath
) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          repository_path: repositoryPath,
        }),
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to create project.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid project response."
    );
  }
}



export async function uploadFiles(
  projectId,
  files
) {
  if (!projectId) {
    throw new Error(
      "A project must be selected before uploading files."
    );
  }

  if (!files || files.length === 0) {
    throw new Error(
      "No files were selected."
    );
  }

  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}/uploads`,
      {
        method: "POST",
        body: formData,
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to upload files.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid upload response."
    );
  }
}

/*
 * Disconnect a project from DevMind.
 */
export async function disconnectProject(
  projectId
) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}/disconnect`,
      {
        method: "POST",
      }
    );
  } catch {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to disconnect project.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid disconnect response."
    );
  }
}

/*
 * Reconnect a project to DevMind.
 */
export async function reconnectProject(
  projectId
) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}/reconnect`,
      {
        method: "POST",
      }
    );
  } catch {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to reconnect project.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid reconnect response."
    );
  }
}

export async function updateProjectKnowledge(projectId) {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/knowledge/update`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    let message = "Failed to update project knowledge.";

    try {
      const error = await response.json();

      if (error?.detail) {
        message = error.detail;
      }
    } catch {
      // Keep the default message.
    }

    throw new Error(message);
  }

  return response.json();
}



export async function getProjectChanges(projectId) {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/changes`
  );

  if (!response.ok) {
    let message = "Failed to check project changes.";

    try {
      const error = await response.json();
      if (error?.detail) {
        message = error.detail;
      }
    } catch {}

    throw new Error(message);
  }

  return response.json();
}


/*
 * Remove a project from DevMind.
 * This removes the project from DevMind's project registry,
 * but does not delete the repository files from the computer.
 */
export async function removeProject(projectId) {
  if (!projectId) {
    throw new Error(
      "A project must be selected."
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}`,
      {
        method: "DELETE",
      }
    );
  } catch {
    throw new Error(
      "Unable to connect to DevMind. Make sure the backend is running."
    );
  }

  if (!response.ok) {
    let errorMessage =
      "Failed to remove project.";

    try {
      const errorData =
        await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorMessage;
      }
    } catch {
      // Ignore JSON parsing errors.
    }

    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch {
    throw new Error(
      "DevMind returned an invalid remove-project response."
    );
  }
}
