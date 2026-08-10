from pathlib import Path

from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.loader.repository_loader import RepositoryLoader

from app.repository_intelligence.analyzers.python_repository_analyzer import (
    PythonRepositoryAnalyzer,
)
from app.repository_intelligence.extractors.ast_extractor import ASTExtractor
from app.repository_intelligence.extractors.import_extractor import ImportExtractor
from app.repository_intelligence.extractors.symbol_extractor import SymbolExtractor
from app.repository_intelligence.graph.relationship_graph import RelationshipGraph
from app.repository_intelligence.models import RelationshipType
from app.repository_intelligence.models import RelationshipType

def test_repository_intelligence_pipeline():

    repository_root = Path.cwd()

    file_filter = FileFilter()

    repository_loader = RepositoryLoader(
        file_filter=file_filter,
    )

    project_files = repository_loader.load(repository_root)

    analyzer = PythonRepositoryAnalyzer(
        ast_extractor=ASTExtractor(),
        symbol_extractor=SymbolExtractor(),
        import_extractor=ImportExtractor(),
        relationship_graph=RelationshipGraph(),
    )

    analysis = analyzer.analyze(
        project_files=project_files,
        repository_root=repository_root,
    )
    assert analysis.metadata.files_analyzed > 0
    assert len(analysis.symbols) > 0
    assert len(analysis.imports) > 0
    assert len(analysis.relationships) > 0

    relationship_types = {
        relationship.relationship_type
        for relationship in analysis.relationships
    }

    assert RelationshipType.DEFINES in relationship_types
    assert RelationshipType.INHERITS in relationship_types
    assert RelationshipType.CALLS in relationship_types
    assert RelationshipType.IMPORTS in relationship_types
    graph = RelationshipGraph()

    call_relationships = [
    relationship
    for relationship in analysis.relationships
    if relationship.relationship_type == RelationshipType.CALLS
]

    assert len(call_relationships) > 0

    call_relationship = call_relationships[0]

    callees = graph.get_callees(
        analysis,
        call_relationship.source_symbol,
    )

    assert any(
        symbol.id == call_relationship.target_symbol
        for symbol in callees
    )

    callers = graph.get_callers(
    analysis,
    call_relationship.target_symbol,
    )

    assert any(
        symbol.id == call_relationship.source_symbol
        for symbol in callers
    )
    print("\n========== Repository Intelligence ==========\n")

    print(f"Repository Root     : {analysis.metadata.root_path}")
    print(f"Language            : {analysis.metadata.language.value}")


    print(f"Files Analysed      : {analysis.metadata.files_analyzed}")
    print(f"Symbols Found       : {len(analysis.symbols)}")
    print(f"Imports Found       : {len(analysis.imports)}")
    print(f"Relationships Found : {len(analysis.relationships)}")

    print("\n----- First 10 Symbols -----")

    for symbol in list(analysis.symbols.values())[:10]:
        print(
            f"{symbol.type.value:<10} "
            f"{symbol.name:<25} "
            f"{symbol.file_path}"
        )

    print("\n----- First 10 Imports -----")

    for statement in analysis.imports[:10]:
        print(
            statement.imported_module,
            statement.imported_name,
        )

    print("\n----- First 10 Relationships -----")

    for relationship in analysis.relationships[:10]:
        print(
            relationship.source_symbol,
            "-->",
            relationship.relationship_type.value,
            "-->",
            relationship.target_symbol,
        )

    print("\n=============================================\n")