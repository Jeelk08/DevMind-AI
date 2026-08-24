function ContextEmptyState({
  title = "No sources used",
  description = "Sources used to answer your questions will appear here.",
}) {
  return (
    <div className="context-panel__empty">
      <div className="context-panel__empty-icon">
        ◌
      </div>

      <h3 className="context-panel__empty-title">
        {title}
      </h3>

      <p className="context-panel__empty-description">
        {description}
      </p>
    </div>
  );
}

export default ContextEmptyState;