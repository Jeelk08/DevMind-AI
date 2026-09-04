import { useState } from "react";
import "./ProjectKnowledgeCard.css";

function ProjectKnowledgeCard({
  project,
  onDisconnect,
  onReconnect,
  onUpdateKnowledge,
  isUpdatingKnowledge = false,
  knowledgeUpdateError = null,
  knowledgeUpdateResult = null,
  projectChanges = null,
  isCheckingChanges = false,
  changeDetectionError = null,
}) {
  const [isUpdatingConnection, setIsUpdatingConnection] =
    useState(false);

  const [showChanges, setShowChanges] = useState(false);

  if (!project) {
    return (
      <section className="project-knowledge-card project-knowledge-card--empty">
        <div className="project-knowledge-card__header">
          <div>
            <span className="project-knowledge-card__eyebrow">
              PROJECT KNOWLEDGE
            </span>

            <h3 className="project-knowledge-card__title">
              No project connected
            </h3>
          </div>
        </div>

        <p className="project-knowledge-card__description">
          Connect a project to let DevMind understand and
          retrieve knowledge from your codebase.
        </p>
      </section>
    );
  }

  const isConnected =
    typeof project.connected === "boolean"
      ? project.connected
      : true;

  /*
   * ---------------------------------------------------------
   * Knowledge statistics
   * ---------------------------------------------------------
   */

  const indexedFiles =
    project.indexed_files ??
    project.files_indexed ??
    project.file_count ??
    null;

  const chunks =
    project.chunks ??
    project.chunk_count ??
    project.total_chunks ??
    null;

  const lastUpdated =
    project.last_updated ??
    project.updated_at ??
    null;

  /*
   * ---------------------------------------------------------
   * Change detection
   * ---------------------------------------------------------
   */

  const addedFiles =
    projectChanges?.added_files ??
    projectChanges?.added ??
    [];

  const modifiedFiles =
    projectChanges?.modified_files ??
    projectChanges?.modified ??
    [];

  const deletedFiles =
    projectChanges?.deleted_files ??
    projectChanges?.deleted ??
    [];

  const addedCount =
    projectChanges?.added_count ??
    (Array.isArray(addedFiles)
      ? addedFiles.length
      : Number(projectChanges?.added ?? 0));

  const modifiedCount =
    projectChanges?.modified_count ??
    (Array.isArray(modifiedFiles)
      ? modifiedFiles.length
      : Number(projectChanges?.modified ?? 0));

  const deletedCount =
    projectChanges?.deleted_count ??
    (Array.isArray(deletedFiles)
      ? deletedFiles.length
      : Number(projectChanges?.deleted ?? 0));

  const totalChanges =
    projectChanges?.total_changes ??
    addedCount +
      modifiedCount +
      deletedCount;

  const changesDetected =
    projectChanges?.status === "changes_detected" ||
    projectChanges?.status === "changes" ||
    totalChanges > 0;

  /*
   * ---------------------------------------------------------
   * Status
   * ---------------------------------------------------------
   */

  const backendStatus =
    project.status ||
    (isConnected ? "Ready" : "Disconnected");

  const normalizedStatus =
    backendStatus.toString().toLowerCase();

  let statusClass = "ready";
  let displayStatus = "Ready";

  if (!isConnected) {
    statusClass = "error";
    displayStatus = "Disconnected";
  } else if (isUpdatingKnowledge) {
    statusClass = "updating";
    displayStatus = "Updating";
  } else if (knowledgeUpdateError) {
    statusClass = "error";
    displayStatus = "Update failed";
  } else if (changesDetected) {
    statusClass = "changes";
    displayStatus = "Changes detected";
  } else if (
    normalizedStatus.includes("error") ||
    normalizedStatus.includes("fail")
  ) {
    statusClass = "error";
    displayStatus = backendStatus;
  } else if (
    normalizedStatus.includes("updat") ||
    normalizedStatus.includes("index") ||
    normalizedStatus.includes("process")
  ) {
    statusClass = "updating";
    displayStatus = backendStatus;
  } else if (
    normalizedStatus.includes("pause")
  ) {
    statusClass = "paused";
    displayStatus = backendStatus;
  } else {
    statusClass = "ready";
    displayStatus = "Ready";
  }

  /*
   * ---------------------------------------------------------
   * Actions
   * ---------------------------------------------------------
   */

  const handleConnectionAction = async () => {
    if (isUpdatingConnection) {
      return;
    }

    const action = isConnected
      ? onDisconnect
      : onReconnect;

    if (!action) {
      return;
    }

    setIsUpdatingConnection(true);

    try {
      await action(project.id);
    } catch (error) {
      console.error(
        "Failed to update project connection:",
        error
      );
    } finally {
      setIsUpdatingConnection(false);
    }
  };

  const handleKnowledgeUpdate = async () => {
    if (
      isUpdatingKnowledge ||
      !onUpdateKnowledge ||
      !isConnected
    ) {
      return;
    }

    try {
      await onUpdateKnowledge(project.id);
    } catch (error) {
      /*
       * The hook already stores the error state.
       * Keep the component from throwing into the UI.
       */
      console.error(
        "Failed to update project knowledge:",
        error
      );
    }
  };

  /*
   * ---------------------------------------------------------
   * Update result
   * ---------------------------------------------------------
   */

  const hasUpdateResult =
    Boolean(knowledgeUpdateResult);

  const updateAdded =
    Number(
      knowledgeUpdateResult?.added ?? 0
    );

  const updateModified =
    Number(
      knowledgeUpdateResult?.modified ?? 0
    );

  const updateDeleted =
    Number(
      knowledgeUpdateResult?.deleted ?? 0
    );

  const updateFailed =
    Number(
      knowledgeUpdateResult?.failed ?? 0
    );

  const hasUpdateChanges =
    updateAdded > 0 ||
    updateModified > 0 ||
    updateDeleted > 0;

  /*
   * ---------------------------------------------------------
   * Helpers
   * ---------------------------------------------------------
   */

  const renderFileList = (
    files,
    prefix
  ) => {
    if (!Array.isArray(files) || files.length === 0) {
      return null;
    }

    return (
      <div className="project-knowledge-card__change-group">
        <div className="project-knowledge-card__change-group-title">
          {prefix === "M"
            ? "Modified"
            : prefix === "+"
            ? "Added"
            : "Deleted"}
        </div>

        <div className="project-knowledge-card__change-files">
          {files.map((file, index) => {
            const fileName =
              typeof file === "string"
                ? file
                : file?.path ??
                  file?.file_path ??
                  file?.fileName ??
                  file?.name ??
                  "Unknown file";

            return (
              <div
                key={`${prefix}-${fileName}-${index}`}
                className="project-knowledge-card__change-file"
              >
                <span className="project-knowledge-card__change-prefix">
                  {prefix}
                </span>

                <span
                  className="project-knowledge-card__change-file-name"
                  title={fileName}
                >
                  {fileName}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <section className="project-knowledge-card">
      {/* -------------------------------------------------- */}
      {/* Header */}
      {/* -------------------------------------------------- */}

      <div className="project-knowledge-card__header">
        <div>
          <span className="project-knowledge-card__eyebrow">
            PROJECT KNOWLEDGE
          </span>

          <h3 className="project-knowledge-card__title">
            {project.name}
          </h3>
        </div>

        <div
          className={`project-knowledge-card__status project-knowledge-card__status--${statusClass}`}
        >
          <span className="project-knowledge-card__status-dot" />

          <span>{displayStatus}</span>
        </div>
      </div>

      {/* -------------------------------------------------- */}
      {/* Knowledge statistics */}
      {/* -------------------------------------------------- */}

      <div className="project-knowledge-card__summary">
        <div className="project-knowledge-card__stat">
          <span className="project-knowledge-card__stat-value">
            {indexedFiles ?? "—"}
          </span>

          <span className="project-knowledge-card__stat-label">
            Files indexed
          </span>
        </div>

        <div className="project-knowledge-card__divider" />

        <div className="project-knowledge-card__stat">
          <span className="project-knowledge-card__stat-value">
            {chunks ?? "—"}
          </span>

          <span className="project-knowledge-card__stat-label">
            Chunks
          </span>
        </div>
      </div>

      {lastUpdated && (
        <div className="project-knowledge-card__updated">
          <span>Last updated</span>

          <strong>{lastUpdated}</strong>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Checking changes */}
      {/* -------------------------------------------------- */}

      {isConnected && isCheckingChanges && (
        <div className="project-knowledge-card__notice">
          <span>
            🔎 Checking for project changes...
          </span>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Change detection error */}
      {/* -------------------------------------------------- */}

      {isConnected && changeDetectionError && (
        <div className="project-knowledge-card__notice">
          <span>
            ⚠ Couldn't check for project changes.
          </span>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Recent changes */}
      {/* -------------------------------------------------- */}

      {isConnected &&
        !isCheckingChanges &&
        changesDetected && (
          <div className="project-knowledge-card__changes">
            <button
              type="button"
              className="project-knowledge-card__changes-toggle"
              onClick={() =>
                setShowChanges((current) => !current)
              }
              aria-expanded={showChanges}
            >
              <span className="project-knowledge-card__changes-summary">
                <span>🟡</span>

                <strong>
                  {totalChanges}{" "}
                  {totalChanges === 1
                    ? "file changed"
                    : "files changed"}
                </strong>
              </span>

              <span className="project-knowledge-card__changes-chevron">
                {showChanges ? "⌃" : "⌄"}
              </span>
            </button>

            {showChanges && (
              <div className="project-knowledge-card__changes-details">
                {renderFileList(
                  modifiedFiles,
                  "M"
                )}

                {renderFileList(
                  addedFiles,
                  "+"
                )}

                {renderFileList(
                  deletedFiles,
                  "−"
                )}

                {/* Count-only fallback */}
                {!Array.isArray(modifiedFiles) &&
                  !Array.isArray(addedFiles) &&
                  !Array.isArray(deletedFiles) && (
                    <div className="project-knowledge-card__change-summary">
                      {modifiedCount > 0 && (
                        <span>
                          {modifiedCount} modified
                        </span>
                      )}

                      {addedCount > 0 && (
                        <span>
                          {addedCount} added
                        </span>
                      )}

                      {deletedCount > 0 && (
                        <span>
                          {deletedCount} deleted
                        </span>
                      )}
                    </div>
                  )}

                {(modifiedCount > 0 ||
                  addedCount > 0 ||
                  deletedCount > 0) && (
                  <div className="project-knowledge-card__change-counts">
                    {modifiedCount > 0 && (
                      <span>
                        {modifiedCount} modified
                      </span>
                    )}

                    {addedCount > 0 && (
                      <span>
                        {addedCount} added
                      </span>
                    )}

                    {deletedCount > 0 && (
                      <span>
                        {deletedCount} deleted
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

      {/* -------------------------------------------------- */}
      {/* Knowledge update error */}
      {/* -------------------------------------------------- */}

      {knowledgeUpdateError && isConnected && (
        <div className="project-knowledge-card__notice">
          <span>
            ⚠ Couldn't update project knowledge.
          </span>

          <button
            type="button"
            className="project-knowledge-card__action"
            onClick={handleKnowledgeUpdate}
            disabled={isUpdatingKnowledge}
          >
            {isUpdatingKnowledge
              ? "Updating..."
              : "Retry"}
          </button>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Knowledge update completed */}
      {/* -------------------------------------------------- */}

      {hasUpdateResult &&
        !knowledgeUpdateError &&
        !isUpdatingKnowledge && (
          <div className="project-knowledge-card__notice">
            <span>
              ✓ Knowledge updated
              {hasUpdateChanges && (
                <>
                  {" · "}
                  {updateAdded} added ·{" "}
                  {updateModified} modified ·{" "}
                  {updateDeleted} deleted
                </>
              )}

              {updateFailed > 0 && (
                <>
                  {" · "}
                  {updateFailed} failed
                </>
              )}
            </span>
          </div>
        )}

      {/* -------------------------------------------------- */}
      {/* Update knowledge */}
      {/* -------------------------------------------------- */}

      {isConnected &&
        !knowledgeUpdateError &&
        !isUpdatingKnowledge &&
        changesDetected && (
          <div className="project-knowledge-card__notice">
            <span>
              Knowledge:
              {" "}
              <strong>🟡 Update available</strong>
            </span>

            <button
              type="button"
              className="project-knowledge-card__action"
              onClick={handleKnowledgeUpdate}
              disabled={isUpdatingKnowledge}
            >
              Update Knowledge
            </button>
          </div>
        )}

      {/* -------------------------------------------------- */}
      {/* Knowledge currently updating */}
      {/* -------------------------------------------------- */}

      {isConnected && isUpdatingKnowledge && (
        <div className="project-knowledge-card__notice">
          <span>
            🔄 DevMind is updating project knowledge.
          </span>

          <button
            type="button"
            className="project-knowledge-card__action"
            disabled
          >
            Updating...
          </button>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Disconnected */}
      {/* -------------------------------------------------- */}

      {!isConnected && (
        <div className="project-knowledge-card__notice">
          <span>
            This project is disconnected. Existing
            project knowledge is preserved.
          </span>

          <button
            type="button"
            className="project-knowledge-card__action"
            onClick={handleConnectionAction}
            disabled={isUpdatingConnection}
          >
            {isUpdatingConnection
              ? "Reconnecting..."
              : "Reconnect"}
          </button>
        </div>
      )}

      {/* -------------------------------------------------- */}
      {/* Connection action */}
      {/* -------------------------------------------------- */}

      {isConnected && !isUpdatingKnowledge && (
        <div className="project-knowledge-card__connection">
          <button
            type="button"
            className="project-knowledge-card__action"
            onClick={handleConnectionAction}
            disabled={isUpdatingConnection}
          >
            {isUpdatingConnection
              ? "Disconnecting..."
              : "Disconnect"}
          </button>
        </div>
      )}
    </section>
  );
}

export default ProjectKnowledgeCard;