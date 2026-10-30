from pathlib import Path


class FileFilter:

    IGNORED_DIRS = {
        ".git",
        ".devmind",
        ".idea",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".coverage",
        "venv",
        ".venv",
        "env",
        "node_modules",
        "dist",
        "build",
    }

    IGNORED_FILES = {
        ".venv",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lock",
        "bun.lockb",
    }

    SUPPORTED_EXTENSIONS = {
        # Python
        ".py",

        # JavaScript / TypeScript
        ".js",
        ".jsx",
        ".ts",
        ".tsx",

        # C / C++
        ".c",
        ".h",
        ".cc",
        ".cpp",
        ".cxx",
        ".hpp",
        ".hh",
        ".hxx",

        # Java
        ".java",

        # Web
        ".html",
        ".css",
        ".scss",

        # Structured data
        ".json",
        ".xml",
        ".yml",
        ".yaml",

        # Documentation
        ".md",
    }

    def should_ignore(self, path: Path) -> bool:

        if path.is_dir():
            return path.name in self.IGNORED_DIRS

        if path.name in self.IGNORED_FILES:
            return True

        return (
            path.suffix.lower()
            not in self.SUPPORTED_EXTENSIONS
        )