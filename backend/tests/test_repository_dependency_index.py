from pathlib import Path

from app.project_knowledge.models import ProjectFile
from app.repository_intelligence.dependency_index import RepositoryDependencyIndex


def test_reverse_javascript_dependency_resolution():
    root = Path('/repo')
    hook = root / 'src' / 'hooks' / 'useDevMind.js'
    context = root / 'src' / 'context' / 'DevMindContext.jsx'
    app = root / 'src' / 'App.jsx'
    files = [
        ProjectFile(hook, 'export default function useDevMind() { return {}; }'),
        ProjectFile(context, 'import useDevMind from "../hooks/useDevMind";\nuseDevMind();'),
        ProjectFile(app, 'import DevMindProvider from "./context/DevMindContext";'),
    ]

    index = RepositoryDependencyIndex(files)
    dependents = index.get_dependents(hook)

    assert [item.source_path for item in dependents] == [context]
    assert dependents[0].reference == '../hooks/useDevMind'


def test_forward_dependencies_and_external_packages():
    root = Path('/repo')
    source = root / 'src' / 'main.js'
    target = root / 'src' / 'utils.js'
    files = [
        ProjectFile(source, 'import React from "react";\nimport { x } from "./utils";'),
        ProjectFile(target, 'export const x = 1;'),
    ]

    index = RepositoryDependencyIndex(files)
    dependencies = index.get_dependencies(source)

    assert len(dependencies) == 1
    assert dependencies[0].target_path == target


def test_missing_or_ambiguous_file_returns_no_match():
    files = [ProjectFile(Path('/repo/a/same.js'), 'export default 1;'),
             ProjectFile(Path('/repo/b/same.js'), 'export default 2;')]
    index = RepositoryDependencyIndex(files)

    assert index.find_file('same.js') is None
    assert index.get_dependents('/repo/missing.js') == []
