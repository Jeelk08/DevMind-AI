function ContextLoading() {
  return (
    <div className="context-panel__loading">
      <div className="context-panel__loading-spinner" />

      <p className="context-panel__loading-text">
        Finding relevant sources...
      </p>
    </div>
  );
}

export default ContextLoading;