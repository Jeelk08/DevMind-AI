import { useState } from "react";
import "./Sidebar.css";
import { useDevMindContext } from "../../context/DevMindContext";
import AddProjectModal from "./AddProjectModal";

function Sidebar() {
  const {
    newChat,
    conversations,
    activeConversationId,
    selectConversation,
    deleteConversation,
    renameConversation,
    projects,
    activeProject,
    switchProject,
    createProject,
  } = useDevMindContext();

  const [editingConversationId, setEditingConversationId] =
    useState(null);

  const [editingTitle, setEditingTitle] =
    useState("");

  const startRenaming = (conversation) => {
    setEditingConversationId(conversation.id);
    setEditingTitle(conversation.title);
  };

  const finishRenaming = () => {
    if (!editingConversationId) {
      return;
    }

    renameConversation(
      editingConversationId,
      editingTitle
    );

    setEditingConversationId(null);
    setEditingTitle("");
  };

  const handleProjectSelect = (project) => {
    switchProject(project);
  };

  const [isAddProjectOpen, setIsAddProjectOpen] =
    useState(false);

  const [isCreatingProject, setIsCreatingProject] =
    useState(false);

  const handleCreateProject = async (
    name,
    repositoryPath
  ) => {
    setIsCreatingProject(true);

    try {
      await createProject(
        name,
        repositoryPath
      );
    } finally {
      setIsCreatingProject(false);
    }
  };

  return (
    <div className="sidebar">
      {/* Brand */}
      <header className="sidebar__header">
        <div className="sidebar__brand">
          <div className="sidebar__brand-mark">
            D
          </div>

          <div className="sidebar__brand-text">
            <span className="sidebar__brand-name">
              DevMind
            </span>

            <span className="sidebar__brand-subtitle">
              AI Second Brain
            </span>
          </div>
        </div>
      </header>

      {/* New conversation */}
      <div className="sidebar__action">
        <button
          className="sidebar__new-chat"
          type="button"
          onClick={newChat}
        >
          <span className="sidebar__new-chat-icon">
            +
          </span>

          <span>New Chat</span>
        </button>
      </div>

      {/* Navigation */}
      <nav
        className="sidebar__navigation"
        aria-label="Sidebar navigation"
      >
        {/* Recent */}
        <section className="sidebar__section">
          <div className="sidebar__section-header">
            <h2 className="sidebar__section-title">
              Recent
            </h2>

          </div>

          <div className="sidebar__items">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`sidebar__conversation ${
                  activeConversationId ===
                  conversation.id
                    ? "sidebar__conversation--active"
                    : ""
                }`}
              >
                {editingConversationId ===
                conversation.id ? (
                  <input
                    className="sidebar__conversation-input"
                    value={editingTitle}
                    autoFocus
                    onChange={(event) =>
                      setEditingTitle(
                        event.target.value
                      )
                    }
                    onBlur={finishRenaming}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        finishRenaming();
                      }

                      if (event.key === "Escape") {
                        setEditingConversationId(
                          null
                        );

                        setEditingTitle("");
                      }
                    }}
                  />
                ) : (
                  <button
                    type="button"
                    className="sidebar__conversation-button"
                    onClick={() =>
                      selectConversation(
                        conversation.id
                      )
                    }
                  >
                    <span className="sidebar__conversation-info">
                      <span className="sidebar__item-label">
                        {conversation.title}
                      </span>

                      <span className="sidebar__conversation-time">
                        {conversation.updatedAt}
                      </span>
                    </span>
                  </button>
                )}

                {!editingConversationId && (
                  <>
                    <button
                      type="button"
                      className="sidebar__conversation-rename"
                      onClick={(event) => {
                        event.stopPropagation();

                        startRenaming(
                          conversation
                        );
                      }}
                      aria-label={`Rename ${conversation.title}`}
                    >
                      ✎
                    </button>

                    <button
                      type="button"
                      className="sidebar__conversation-delete"
                      onClick={(event) => {
                        event.stopPropagation();

                        deleteConversation(
                          conversation.id
                        );
                      }}
                      aria-label={`Delete ${conversation.title}`}
                    >
                      ×
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Pinned */}
        <section className="sidebar__section">
          <h2 className="sidebar__section-title">
            Pinned
          </h2>

          <div className="sidebar__items">
            <button
              type="button"
              className="sidebar__item"
            >
              <span className="sidebar__item-icon">
                📌
              </span>

              <span className="sidebar__item-label">
                DevMind Architecture
              </span>
            </button>
          </div>
        </section>

        {/* Projects */}
        <section className="sidebar__section">
          <h2 className="sidebar__section-title">
            Projects
          </h2>
          <button
            type="button"
            className="sidebar__section-add"
            aria-label="Add project"
            onClick={() =>
              setIsAddProjectOpen(true)
            }
          >
            +
          </button>

          <div className="sidebar__items">
            {projects.length === 0 ? (
              <div className="sidebar__item">
                <span className="sidebar__item-icon">
                  🧠
                </span>

                <span className="sidebar__item-label">
                  Loading projects...
                </span>
              </div>
            ) : (
              projects.map((project) => {
                const isActive =
                  project.id ===
                  activeProject?.id;

                return (
                  <button
                    key={project.id}
                    type="button"
                    className={`sidebar__item ${
                      isActive
                        ? "sidebar__item--active"
                        : ""
                    }`}
                    onClick={() =>
                      handleProjectSelect(
                        project
                      )
                    }
                  >
                    <span className="sidebar__item-icon">
                      🧠
                    </span>

                    <span className="sidebar__item-label">
                      {project.name}
                    </span>
                  </button>
                );
              })
            )}
          </div>
        </section>

        {/* General */}
        <section className="sidebar__section">
          <h2 className="sidebar__section-title">
            General
          </h2>

          <div className="sidebar__items">
            <button
              type="button"
              className="sidebar__item"
            >
              <span className="sidebar__item-label">
                FastAPI question
              </span>
            </button>

            <button
              type="button"
              className="sidebar__item"
            >
              <span className="sidebar__item-label">
                Python help
              </span>
            </button>
          </div>
        </section>
      </nav>

      {/* Bottom */}
      <footer className="sidebar__footer">
        <button
          type="button"
          className="sidebar__settings"
        >
          <span className="sidebar__settings-icon">
            ⚙
          </span>

          <span>Settings</span>
        </button>
      </footer>
      {isAddProjectOpen && (
        <AddProjectModal
          onClose={() =>
            setIsAddProjectOpen(false)
          }
          onCreate={handleCreateProject}
          isCreating={isCreatingProject}
        />
      )}
    </div>
  );
}

export default Sidebar;