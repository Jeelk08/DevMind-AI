import { useEffect, useState } from "react";
import "./ContextPanel.css";

import ContextSource from "./source/ContextSource";
import SourceDetails from "./source/SourceDetails";
import ContextEmptyState from "./ContextEmptyState";
import ContextLoading from "./ContextLoading";
import { useDevMindContext } from "../../context/DevMindContext";

function ContextPanel() {
  const [selectedSource, setSelectedSource] =
    useState(null);

  const {
    activeProject,
    contextState,
    contextSources,
    contextQuery,
  } = useDevMindContext();

  useEffect(() => {
    setSelectedSource(null);
  }, [activeProject?.id, contextQuery]);


  if (selectedSource) {
    return (
      <SourceDetails
        fileName={selectedSource.fileName}
        filePath={selectedSource.filePath}
        relevance={selectedSource.relevance}
        content={selectedSource.content}
        onClose={() => setSelectedSource(null)}
      />
    );
  }

  return (
    <div className="context-panel">
      {/* Header */}
      <header className="context-panel__header">
        <div>
          <h2 className="context-panel__title">
            Context
          </h2>

          <p className="context-panel__subtitle">
            Active knowledge for this conversation
          </p>

          {contextQuery && (
            <div className="context-panel__query">
              <span className="context-panel__query-label">
                Query
              </span>

              <span
                className="context-panel__query-text"
                title={contextQuery}
              >
                {contextQuery}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Active context */}
      <section className="context-panel__section">
        <div className="context-panel__section-header">
          <h3 className="context-panel__section-title">
            Active Context
          </h3>

          <span className="context-panel__count">
            {activeProject ? 1 : 0}
          </span> 
        </div>

        {activeProject ? (
          <div className="context-panel__context-card">
            <div className="context-panel__context-icon">
              🧠
            </div>

            <div className="context-panel__context-info">
              <span className="context-panel__context-name">
                {activeProject.name}
              </span>

              <span className="context-panel__context-status">
                {activeProject.status ||
                  "Knowledge up to date"}
              </span>
            </div>

            <span className="context-panel__status-dot" />
          </div>
        ) : (
          <div className="context-panel__context-card">
            <div className="context-panel__context-icon">
              🧠
            </div>

            <div className="context-panel__context-info">
              <span className="context-panel__context-name">
                Loading projects...
              </span>

              <span className="context-panel__context-status">
                Please wait
              </span>
            </div>
          </div>
        )}
      </section>

      {/* Sources */}
      <section className="context-panel__section">
        <div className="context-panel__section-header">
          <h3 className="context-panel__section-title">
            Sources
          </h3>

          {contextState === "sources" && (
            <span className="context-panel__count">
              {contextSources.length}
            </span>
          )}
        </div>

        {contextState === "loading" && (
          <ContextLoading />
        )}

        {contextState === "empty" && (
          <ContextEmptyState />
        )}

        {contextState === "sources" && (
          <div className="context-panel__sources">
            {contextSources.map((source) => (
              <div
                key={source.id}
                className="context-panel__source-item"
                onClick={() =>
                  setSelectedSource(source)
                }
                role="button"
                tabIndex={0}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();

                    setSelectedSource(source);
                  }
                }}
              >
                <ContextSource
                  fileName={source.fileName}
                  filePath={source.filePath}
                  relevance={source.relevance}
                />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default ContextPanel;