
import { useEffect, useRef, useState } from "react";
import {
  playCompletionSound,
  unlockCompletionSound,
} from "./completionSound";

import "./OperationCenter.css";
import { useDevMindContext } from "../../context/DevMindContext";

function OperationCenter({ folderOperation }) {
  const {
    isUploading,
    isUpdatingKnowledge,
    knowledgeUpdateError,
    knowledgeUpdateResult,
  } = useDevMindContext();

  const [isExpanded, setIsExpanded] = useState(false);
  const [successDismissed, setSuccessDismissed] = useState(false);

  const previousState = useRef({
    folderComplete: false,
    knowledgeUpdating: false,
  });

  // Unlock browser audio after the first user interaction.
  useEffect(() => {
    const handleUserGesture = () => unlockCompletionSound();

    window.addEventListener("pointerdown", handleUserGesture, {
      passive: true,
    });

    window.addEventListener("keydown", handleUserGesture);

    return () => {
      window.removeEventListener("pointerdown", handleUserGesture);
      window.removeEventListener("keydown", handleUserGesture);
    };
  }, []);

  // Detect successful completion and play sound once.
  useEffect(() => {
    const folderComplete = Boolean(
      folderOperation?.complete && !folderOperation?.error
    );

    const knowledgeJustCompleted =
      previousState.current.knowledgeUpdating &&
      !isUpdatingKnowledge &&
      Boolean(knowledgeUpdateResult) &&
      !knowledgeUpdateError;

    const folderJustCompleted =
      folderComplete &&
      !previousState.current.folderComplete;

    if (folderJustCompleted || knowledgeJustCompleted) {
      playCompletionSound();
    }

    previousState.current = {
      folderComplete,
      knowledgeUpdating: Boolean(isUpdatingKnowledge),
    };
  }, [
    folderOperation?.complete,
    folderOperation?.error,
    isUpdatingKnowledge,
    knowledgeUpdateResult,
    knowledgeUpdateError,
  ]);

  // Automatically dismiss successful operation notifications.
  useEffect(() => {
    const folderInProgress =
      folderOperation?.active &&
      !folderOperation?.complete &&
      !folderOperation?.error;

    const operationRunning =
      isUpdatingKnowledge || isUploading || folderInProgress;

    if (operationRunning) {
      setSuccessDismissed(false);
      return;
    }

    const operationSucceeded =
      !knowledgeUpdateError &&
      (
        Boolean(knowledgeUpdateResult) ||
        Boolean(folderOperation?.complete && !folderOperation?.error)
      );

    if (!operationSucceeded) return;

    const timer = window.setTimeout(() => {
      setSuccessDismissed(true);
    }, 3500);

    return () => window.clearTimeout(timer);
  }, [
    isUpdatingKnowledge,
    isUploading,
    Boolean(knowledgeUpdateResult),
    knowledgeUpdateError,
    folderOperation?.active,
    folderOperation?.complete,
    folderOperation?.error,
  ]);

  let title = "";
  let message = "";
  let statusClass = "working";
  let phase = "";
  let progress = null;

  if (folderOperation?.active) {
    title = folderOperation.title || "Importing project";
    message =
      folderOperation.message || "Working on your project...";

    phase = folderOperation.phase || "";
    progress = folderOperation.progress ?? null;

    statusClass = folderOperation.error
      ? "error"
      : folderOperation.complete
        ? "success"
        : "working";
  } else if (isUpdatingKnowledge) {
    title = "Updating project knowledge";
    message = "Scanning changes and refreshing the knowledge index...";
    phase = "indexing";
  } else if (isUploading) {
    title = "Uploading files";
    message = "Adding files to project knowledge...";
    phase = "uploading";
  } else if (knowledgeUpdateError) {
    title = "Knowledge update failed";
    message = knowledgeUpdateError;
    statusClass = "error";
  } else if (knowledgeUpdateResult) {
    title = "Knowledge updated";
    message = "Project knowledge is up to date.";
    statusClass = "success";
  } else {
    return null;
  }

  // Hide successful notifications after the timeout.
  if (statusClass === "success" && successDismissed) {
    return null;
  }

  const isWorking = statusClass === "working";

  return (
    <section
      className={`operation-center operation-center--${statusClass} ${
        isExpanded ? "operation-center--expanded" : ""
      }`}
      role="status"
      aria-live="polite"
    >
      <button
        type="button"
        className="operation-center__main"
        onClick={() => setIsExpanded((value) => !value)}
        aria-expanded={isExpanded}
        aria-label={
          isExpanded
            ? "Collapse operation details"
            : "Expand operation details"
        }
      >
        <span className="operation-center__indicator">
          {isWorking ? (
            <span className="operation-center__spinner" />
          ) : statusClass === "error" ? (
            "!"
          ) : (
            "✓"
          )}
        </span>

        <span className="operation-center__content">
          <strong className="operation-center__title">
            {title}
          </strong>

          <span className="operation-center__message">
            {message}
          </span>
        </span>

        {progress !== null && isWorking && (
          <span className="operation-center__percent">
            {Math.round(progress)}%
          </span>
        )}

        <span className="operation-center__chevron">
          {isExpanded ? "⌃" : "⌄"}
        </span>
      </button>

      {isWorking && (
        <div
          className="operation-center__track"
          aria-hidden="true"
        >
          {progress === null ? (
            <span className="operation-center__track-indeterminate" />
          ) : (
            <span
              className="operation-center__track-fill"
              style={{
                width: `${Math.max(
                  0,
                  Math.min(100, progress)
                )}%`,
              }}
            />
          )}
        </div>
      )}

      {isExpanded && (
        <div className="operation-center__details">
          {phase && (
            <span className="operation-center__phase">
              {phase}
            </span>
          )}

          {folderOperation?.filesFound != null && (
            <span>
              {folderOperation.filesFound.toLocaleString()} supported
              files discovered
            </span>
          )}

          {folderOperation?.filesTotal != null && (
            <span>
              {folderOperation.filesTotal.toLocaleString()} files
              selected for upload
            </span>
          )}
        </div>
      )}
    </section>
  );
}

export default OperationCenter;
