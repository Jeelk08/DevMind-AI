import "./OperationCenter.css";

import { useDevMindContext } from "../../context/DevMindContext";

function OperationCenter() {
  const {
    isUploading,
    isUpdatingKnowledge,
    knowledgeUpdateError,
    knowledgeUpdateResult,
  } = useDevMindContext();

  const isWorking =
    isUploading || isUpdatingKnowledge;

  if (!isWorking && !knowledgeUpdateError && !knowledgeUpdateResult) {
    return null;
  }

  let title = "DevMind";
  let message = "";
  let statusClass = "success";

  if (isUploading) {
    title = "Uploading files";
    message = "Adding files to project knowledge...";
    statusClass = "working";
  } else if (isUpdatingKnowledge) {
    title = "Updating knowledge";
    message = "Refreshing project knowledge...";
    statusClass = "working";
  } else if (knowledgeUpdateError) {
    title = "Knowledge update failed";
    message = "Something went wrong while updating.";
    statusClass = "error";
  } else if (knowledgeUpdateResult) {
    title = "Knowledge updated";
    message = "Project knowledge is up to date.";
    statusClass = "success";
  }

  return (
    <div
      className={`operation-center operation-center--${statusClass}`}
      role="status"
      aria-live="polite"
    >
      <span className="operation-center__indicator">
        {statusClass === "working"
          ? "↻"
          : statusClass === "error"
          ? "!"
          : "✓"}
      </span>

      <div className="operation-center__content">
        <strong className="operation-center__title">
          {title}
        </strong>

        <span className="operation-center__message">
          {message}
        </span>
      </div>
    </div>
  );
}

export default OperationCenter;