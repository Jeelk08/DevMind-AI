import { useEffect, useRef, useState } from "react";
import "./ProjectSwitcher.css";

function ProjectSwitcher({
  projects = [],
  activeProject = null,
  onProjectChange,
  onDisconnect,
  onReconnect,
  onRemove,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isUpdatingConnection, setIsUpdatingConnection] =
    useState(false);

  const switcherRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        switcherRef.current &&
        !switcherRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  const handleProjectSelect = (project) => {
    setIsOpen(false);

    onProjectChange?.(project);
  };

  const handleDisconnect = async () => {
    if (
      !activeProject?.id ||
      isUpdatingConnection ||
      !onDisconnect
    ) {
      return;
    }

    setIsUpdatingConnection(true);

    try {
      await onDisconnect(activeProject.id);
    } catch (error) {
      console.error(
        "Failed to disconnect project:",
        error
      );
    } finally {
      setIsUpdatingConnection(false);
    }
  };

  const handleReconnect = async () => {
    if (
      !activeProject?.id ||
      isUpdatingConnection ||
      !onReconnect
    ) {
      return;
    }

    setIsUpdatingConnection(true);

    try {
      await onReconnect(activeProject.id);
    } catch (error) {
      console.error(
        "Failed to reconnect project:",
        error
      );
    } finally {
      setIsUpdatingConnection(false);
    }
  };

  if (!activeProject) {
    return (
      <div
        ref={switcherRef}
        className="project-switcher"
      >
        <div className="project-switcher__trigger">
          <span className="project-switcher__icon">
            🧠
          </span>

          <span className="project-switcher__info">
            <span className="project-switcher__name">
              Loading projects...
            </span>

            <span className="project-switcher__status">
              Please wait
            </span>
          </span>
        </div>
      </div>
    );
  }

  const handleRemove = async () => {
    if (
      !activeProject?.id ||
      isUpdatingConnection ||
      !onRemove
    ) {
      return;
    }

    const confirmed = window.confirm(
      `Remove "${activeProject.name}" from DevMind AI?\n\nThis will remove the project from DevMind, but will not delete the repository files from your computer.`
    );

    if (!confirmed) {
      return;
    }

    setIsUpdatingConnection(true);

    try {
      await onRemove(activeProject.id);
      setIsOpen(false);
    } catch (error) {
      console.error(
        "Failed to remove project:",
        error
      );
    } finally {
      setIsUpdatingConnection(false);
    }
  };

  const isConnected =
    activeProject.connected !== false;

  return (
    <div
      ref={switcherRef}
      className="project-switcher"
    >
      <button
        type="button"
        className="project-switcher__trigger"
        onClick={() =>
          setIsOpen((open) => !open)
        }
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        <span className="project-switcher__icon">
          🧠
        </span>

        <span className="project-switcher__info">
          <span className="project-switcher__name">
            {activeProject.name}
          </span>

          <span className="project-switcher__status">
            {isConnected
              ? activeProject.status ||
                "Knowledge up to date"
              : "Disconnected"}
          </span>
        </span>

        <span
          className={`project-switcher__connection ${
            isConnected
              ? "project-switcher__connection--connected"
              : "project-switcher__connection--disconnected"
          }`}
          title={
            isConnected
              ? "Project connected"
              : "Project disconnected"
          }
          aria-label={
            isConnected
              ? "Project connected"
              : "Project disconnected"
          }
        />

        <span
          className={`project-switcher__arrow ${
            isOpen
              ? "project-switcher__arrow--open"
              : ""
          }`}
        >
          ▾
        </span>
      </button>

      {isOpen && (
        <div
          className="project-switcher__menu"
          role="menu"
        >
          <div className="project-switcher__menu-header">
            <span>Projects</span>
          </div>

          {projects.map((project) => {
            const isActive =
              project.id === activeProject.id;

            const projectConnected =
              project.connected !== false;

            return (
              <button
                key={project.id}
                type="button"
                className={`project-switcher__item ${
                  isActive
                    ? "project-switcher__item--active"
                    : ""
                }`}
                onClick={() =>
                  handleProjectSelect(project)
                }
                role="menuitem"
              >
                <span className="project-switcher__item-icon">
                  📁
                </span>

                <span className="project-switcher__item-info">
                  <span className="project-switcher__item-name">
                    {project.name}
                  </span>

                  <span className="project-switcher__item-status">
                    {projectConnected
                      ? project.status ||
                        "Knowledge up to date"
                      : "Disconnected"}
                  </span>
                </span>

                <span
                  className={`project-switcher__item-connection ${
                    projectConnected
                      ? "project-switcher__item-connection--connected"
                      : "project-switcher__item-connection--disconnected"
                  }`}
                />

                {isActive && (
                  <span className="project-switcher__check">
                    ✓
                  </span>
                )}
              </button>
            );
          })}

          <div className="project-switcher__divider" />

          <div className="project-switcher__actions">
            {isConnected ? (
              <button
                type="button"
                className="project-switcher__connection-action project-switcher__connection-action--disconnect"
                onClick={handleDisconnect}
                disabled={isUpdatingConnection}
              >
                <span>
                  {isUpdatingConnection
                    ? "Disconnecting..."
                    : "Disconnect project"}
                </span>
              </button>
            ) : (
              <button
                type="button"
                className="project-switcher__connection-action project-switcher__connection-action--reconnect"
                onClick={handleReconnect}
                disabled={isUpdatingConnection}
              >
                <span>
                  {isUpdatingConnection
                    ? "Reconnecting..."
                    : "Reconnect project"}
                </span>
              </button>
            )}
              <button
                type="button"
                className="project-switcher__connection-action project-switcher__connection-action--remove"
                onClick={handleRemove}
                disabled={isUpdatingConnection}
              >
                <span>
                  {isUpdatingConnection
                    ? "Removing..."
                    : "Remove project"}
                </span>
              </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProjectSwitcher;