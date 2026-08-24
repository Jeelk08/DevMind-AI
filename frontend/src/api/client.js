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


export async function retrieveContext(query, projectId) {
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