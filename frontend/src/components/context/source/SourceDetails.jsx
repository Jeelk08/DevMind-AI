import "./SourceDetails.css";

function SourceDetails({
  fileName,
  filePath,
  content,
  onClose,
}) {
  return (
    <aside className="source-details">
      <header className="source-details__header">
        <div className="source-details__title-group">
          <span className="source-details__icon">
            📄
          </span>

          <div>
            <h3 className="source-details__name">
              {fileName}
            </h3>

            <p className="source-details__path">
              {filePath}
            </p>
          </div>
        </div>

        <button
          type="button"
          className="source-details__close"
          onClick={onClose}
          aria-label="Close source details"
        >
          ×
        </button>
      </header>

      <div className="source-details__body">
        <section className="source-details__section source-details__section--content">
          <span className="source-details__label">
            Retrieved context
          </span>

          <div className="source-details__content">
            {content}
          </div>
        </section>
      </div>
    </aside>
  );
}

export default SourceDetails;