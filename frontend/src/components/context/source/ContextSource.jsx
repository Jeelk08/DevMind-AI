import "./ContextSource.css";

function ContextSource({
  fileName,
  filePath,
  type = "file",
}) {
  return (
    <article className="context-source">
      <div className="context-source__icon">
        {type === "file" ? (
          "📄"
        ) : (
          <img
            src="/devmind-brain.png"
            alt="DevMind"
            className="devmind-brain-icon"
          />
        )}
      </div>

      <div className="context-source__info">
        <span className="context-source__name">
          {fileName}
        </span>

        <span
          className="context-source__path"
          title={filePath}
        >
          {filePath}
        </span>
      </div>

      <button
        className="context-source__action"
        type="button"
        aria-label={`Open ${fileName}`}
      >
        →
      </button>
    </article>
  );
}

export default ContextSource;