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
        ".py",
        ".java",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".html",
        ".css",
        ".json",
        ".md",
        ".yml",
        ".yaml",
    }

    def should_ignore(self, path: Path) -> bool:

        if path.is_dir():
            return path.name in self.IGNORED_DIRS

        if path.name in self.IGNORED_FILES:
            return True

        return path.suffix.lower() not in self.SUPPORTED_EXTENSIONS