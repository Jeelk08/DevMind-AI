import { useEffect, useState } from "react";
import "./ContextPanel.css";

import ContextSource from "./source/ContextSource";
import SourceDetails from "./source/SourceDetails";
import ContextEmptyState from "./ContextEmptyState";
import ContextLoading from "./ContextLoading";
import ProjectKnowledgeCard from "../project/ProjectKnowledgeCard";
import { useDevMindContext } from "../../context/DevMindContext";

const PANEL_TABS = [
  { id: "overview", label: "Overview", icon: "◈" },
  { id: "indexing", label: "Indexing Scope", icon: "▦" },
  { id: "sources", label: "Sources", icon: "⌘" },
];

function ContextPanel() {
  const [selectedSource, setSelectedSource] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

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
      <div className="context-panel">
        <SourceDetails
          fileName={selectedSource.fileName}
          filePath={selectedSource.filePath}
          relevance={selectedSource.relevance}
          content={selectedSource.content}
          onClose={() => setSelectedSource(null)}
        />
      </div>
    );
  }

  return (
    <div className="context-panel">
      <header className="context-panel__header">
        <div>
          <p className="context-panel__eyebrow">PROJECT WORKSPACE</p>
          <h2 className="context-panel__title">
            {activeTab === "overview"
              ? "Project Overview"
              : activeTab === "indexing"
                ? "Indexing Scope"
                : "Sources"}
          </h2>
          <p className="context-panel__subtitle">
            {activeTab === "overview"
              ? "Project health and knowledge status"
              : activeTab === "indexing"
                ? "Files included in repository knowledge"
                : "Code retrieved for the current conversation"}
          </p>
          {activeProject && (
            <div className="context-panel__project-label">
              <span className="context-panel__project-dot" />
              <span>{activeProject.name}</span>
            </div>
          )}
          {contextQuery && (
            <div className="context-panel__query">
              <span className="context-panel__query-label">CURRENT QUERY</span>
              <span className="context-panel__query-text" title={contextQuery}>
                {contextQuery}
              </span>
            </div>
          )}
        </div>
      </header>

      <div className="context-panel__content">
        {activeTab === "overview" && (
          <>
            <section className="context-panel__section context-panel__overview-section">
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

            <section className="context-panel__section">
              <div className="context-panel__section-header">
                <h3 className="context-panel__section-title">Active Context</h3>
                <span className="context-panel__count">{activeProject ? 1 : 0}</span>
              </div>
              {activeProject ? (
                <div className="context-panel__context-card">
                  <div className="context-panel__context-icon">
                    <img
                      src="/devmind-brain1.png"
                      alt="DevMind"
                      className="devmind-brain-icon"
                    />
                  </div>
                  <div className="context-panel__context-info">
                    <span className="context-panel__context-name">{activeProject.name}</span>
                    <span className="context-panel__context-status">
                      {activeProject.connected === false
                        ? "Project disconnected"
                        : activeProject.status || "Knowledge up to date"}
                    </span>
                  </div>
                  <span className="context-panel__status-dot" />
                </div>
              ) : (
                <div className="context-panel__context-card">
                  <div className="context-panel__context-icon">
                    <img
                      src="/devmind-brain.png"
                      alt="DevMind"
                      className="devmind-brain-icon"
                    />
                  </div>
                  <div className="context-panel__context-info">
                    <span className="context-panel__context-name">No project connected</span>
                    <span className="context-panel__context-status">
                      Connect a project to use project knowledge
                    </span>
                  </div>
                </div>
              )}
            </section>
          </>
        )}

        {activeTab === "indexing" && (
          <section className="context-panel__section">
            <div className="context-panel__section-header">
              <h3 className="context-panel__section-title">Indexed repository</h3>
            </div>
            <div className="context-panel__scope-card">
              <div className="context-panel__scope-icon">📁</div>
              <div className="context-panel__scope-info">
                <span className="context-panel__scope-name">Repository files</span>
                <span className="context-panel__scope-description">
                  Supported source files from the connected project are indexed as project knowledge.
                </span>
                {activeProject?.repository_path && (
                  <span
                    className="context-panel__scope-path"
                    title={activeProject.repository_path}
                  >
                    {activeProject.repository_path}
                  </span>
                )}
                {!activeProject && (
                  <span className="context-panel__scope-description">
                    Connect a project to see its indexing location.
                  </span>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "sources" && (
          <section className="context-panel__section context-panel__sources-section">
            <div className="context-panel__section-header">
              <h3 className="context-panel__section-title">Retrieved sources</h3>
              <span className="context-panel__count">
                {contextState === "sources" ? contextSources.length : 0}
              </span>
            </div>
            {contextState === "loading" && <ContextLoading />}
            {contextState === "empty" && <ContextEmptyState />}
            {contextState === "sources" && contextSources.length > 0 && (
              <div className="context-panel__sources">
                {contextSources.map((source) => (
                  <div
                    key={source.id}
                    className="context-panel__source-item"
                    onClick={() => setSelectedSource(source)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
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
            {contextState === "sources" && contextSources.length === 0 && (
              <ContextEmptyState />
            )}
          </section>
        )}
      </div>

      <nav className="context-panel__bottom-nav" aria-label="Project panel sections">
        {PANEL_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`context-panel__tab ${activeTab === tab.id ? "context-panel__tab--active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
            aria-current={activeTab === tab.id ? "page" : undefined}
          >
            <span className="context-panel__tab-icon" aria-hidden="true">{tab.icon}</span>
            <span className="context-panel__tab-label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

export default ContextPanel;
