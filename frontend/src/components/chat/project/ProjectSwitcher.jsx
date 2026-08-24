import { useEffect, useRef, useState } from "react";
import "./ProjectSwitcher.css";

function ProjectSwitcher({
  projects = [],
  activeProject = null,
  onProjectChange,
}) {
  const [isOpen, setIsOpen] = useState(false);

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

  return (
    <div
      ref={switcherRef}
      className="project-switcher"
    >
      <button
        type="button"
        className="project-switcher__trigger"
        onClick={() => setIsOpen((open) => !open)}
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
            {activeProject.status ||
              "Knowledge up to date"}
          </span>
        </span>

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
            Projects
          </div>

          {projects.map((project) => {
            const isActive =
              project.id === activeProject.id;

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
                    {project.status ||
                      "Knowledge up to date"}
                  </span>
                </span>

                {isActive && (
                  <span className="project-switcher__check">
                    ✓
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ProjectSwitcher;