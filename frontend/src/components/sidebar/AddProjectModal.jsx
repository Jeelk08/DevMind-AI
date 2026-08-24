import { useState } from "react";
import "./AddProjectModal.css";

function AddProjectModal({
  onClose,
  onCreate,
  isCreating = false,
}) {
  const [name, setName] = useState("");
  const [repositoryPath, setRepositoryPath] =
    useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedName = name.trim();
    const trimmedPath = repositoryPath.trim();

    if (!trimmedName) {
      setError("Project name is required.");
      return;
    }

    if (!trimmedPath) {
      setError("Repository path is required.");
      return;
    }

    setError("");

    try {
      await onCreate(
        trimmedName,
        trimmedPath
      );

      onClose();
    } catch (error) {
      setError(
        error.message ||
          "Failed to create project."
      );
    }
  };

  return (
    <div
      className="add-project-modal__overlay"
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget &&
          !isCreating
        ) {
          onClose();
        }
      }}
    >
      <div
        className="add-project-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-project-title"
      >
        <header className="add-project-modal__header">
          <div>
            <h2 id="add-project-title">
              Add Project
            </h2>

            <p>
              Connect a local repository to
              DevMind.
            </p>
          </div>

          <button
            type="button"
            className="add-project-modal__close"
            onClick={onClose}
            disabled={isCreating}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <form
          className="add-project-modal__form"
          onSubmit={handleSubmit}
        >
          <label>
            <span>Project Name</span>

            <input
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="e.g. My Portfolio"
              disabled={isCreating}
              autoFocus
            />
          </label>

          <label>
            <span>Repository Path</span>

            <input
              type="text"
              value={repositoryPath}
              onChange={(event) =>
                setRepositoryPath(
                  event.target.value
                )
              }
              placeholder="V:\Code\MyProject"
              disabled={isCreating}
            />
          </label>

          {error && (
            <p className="add-project-modal__error">
              {error}
            </p>
          )}

          <div className="add-project-modal__actions">
            <button
              type="button"
              onClick={onClose}
              disabled={isCreating}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isCreating}
            >
              {isCreating
                ? "Connecting..."
                : "Connect Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddProjectModal;