import { useEffect, useState } from "react";
import "./ContextPanel.css";

import ContextSource from "./source/ContextSource";
import SourceDetails from "./source/SourceDetails";
import ContextEmptyState from "./ContextEmptyState";
import ContextLoading from "./ContextLoading";
import ProjectKnowledgeCard from "../project/ProjectKnowledgeCard";

import { useDevMindContext } from "../../context/DevMindContext";

function ContextPanel() {
  const [selectedSource, setSelectedSource] = useState(null);

  const {
    activeProject,
    contextState,
    contextSources,
    contextQuery,
    disconnectProject,
    reconnectProject,

    updateProjectKnowledge,
    isUpdatingKnowledge,
    knowledgeUpdateError,
    knowledgeUpdateResult,

    projectChanges,
    isCheckingChanges,
    changeDetectionError,
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
            Project Overview
          </h2>

          <p className="context-panel__subtitle">
            Project knowledge and active context
          </p>

          {activeProject && (
            <div className="context-panel__project-label">
              <span className="context-panel__project-dot" />
              <span>{activeProject.name}</span>
            </div>
          )}

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

      {/* Project Knowledge */}
      <section className="context-panel__section">
        <ProjectKnowledgeCard
          project={activeProject}
          onDisconnect={disconnectProject}
          onReconnect={reconnectProject}
          onUpdateKnowledge={updateProjectKnowledge}
          isUpdatingKnowledge={isUpdatingKnowledge}
          knowledgeUpdateError={knowledgeUpdateError}
          knowledgeUpdateResult={knowledgeUpdateResult}
          projectChanges={projectChanges}
          isCheckingChanges={isCheckingChanges}
          changeDetectionError={changeDetectionError}
        />
      </section>



      {/* Indexing Scope */}
      <section className="context-panel__section">
        <div className="context-panel__section-header">
          <h3 className="context-panel__section-title">
            Indexing Scope
          </h3>
        </div>

        <div className="context-panel__scope-card">
          <div className="context-panel__scope-icon">
            📁
          </div>

          <div className="context-panel__scope-info">
            <span className="context-panel__scope-name">
              Repository files
            </span>

            <span className="context-panel__scope-description">
              Supported source files from the connected project
              are indexed as project knowledge.
            </span>

            {activeProject?.repository_path && (
              <span
                className="context-panel__scope-path"
                title={activeProject.repository_path}
              >
                {activeProject.repository_path}
              </span>
            )}
          </div>
        </div>
      </section>



      {/* Active Context */}
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
                {activeProject.connected === false
                  ? "Project disconnected"
                  : activeProject.status ||
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
                No project connected
              </span>

              <span className="context-panel__context-status">
                Connect a project to use project knowledge
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
                onClick={() => setSelectedSource(source)}
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

      {/* Project Settings */}
      <section className="context-panel__section">
        <div className="context-panel__section-header">
          <h3 className="context-panel__section-title">
            Project Settings
          </h3>
        </div>

        <div className="context-panel__settings-card">
          <div className="context-panel__settings-info">
            <span className="context-panel__settings-name">
              Repository connection
            </span>

            <span className="context-panel__settings-description">
              {activeProject
                ? activeProject.connected === false
                  ? "This project is currently disconnected."
                  : "DevMind is connected to this project's repository."
                : "No project is currently connected."}
            </span>
          </div>

          {activeProject && (
            <span
              className={`context-panel__settings-status ${
                activeProject.connected === false
                  ? "context-panel__settings-status--disconnected"
                  : "context-panel__settings-status--connected"
              }`}
            >
              {activeProject.connected === false
                ? "Disconnected"
                : "Connected"}
            </span>
          )}
        </div>
      </section>
    </div>
  );
}



export default ContextPanel;