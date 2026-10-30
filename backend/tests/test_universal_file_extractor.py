from pathlib import Path

from app.repository_intelligence.extractors.universal_file_extractor import (
    UniversalFileExtractor,
)

from app.project_knowledge.loader.file_filter import (
    FileFilter,
)


def test_python_and_javascript_imports():

    extractor = UniversalFileExtractor()

    py = extractor.extract(
        Path("service.py"),
        "from pathlib import Path\nimport os\n",
    )

    js = extractor.extract(
        Path("app.js"),
        "import React from 'react';\n"
        "const api = require('axios');\n",
    )

    assert "pathlib" in py.references
    assert "os" in py.references
    assert "react" in js.references
    assert "axios" in js.references


def test_cpp_includes_and_html_references():

    extractor = UniversalFileExtractor()

    cpp = extractor.extract(
        Path("main.cpp"),
        '#include <iostream>\n#include "utils.h"\n',
    )

    html = extractor.extract(
        Path("index.html"),
        '<script src="app.js"></script>'
        '<link href="site.css">',
    )

    assert cpp.references == [
        "iostream",
        "utils.h",
    ]

    assert "app.js" in html.references
    assert "site.css" in html.references


def test_css_json_and_xml_structure():

    extractor = UniversalFileExtractor()

    css = extractor.extract(
        Path("site.css"),
        "@import './base.css';\n"
        ".card { color: red; }",
    )

    data = extractor.extract(
        Path("config.json"),
        '{"app": {"name": "DevMind"}}',
    )

    xml = extractor.extract(
        Path("config.xml"),
        '<root><item href="data.json" /></root>',
    )

    assert "./base.css" in css.references

    assert (
        "JSON key: $.app.name"
        in data.structures
    )

    assert "data.json" in xml.references
    assert "XML element: item" in xml.structures


def test_filter_includes_requested_common_extensions():

    file_filter = FileFilter()

    filenames = (
        "index.html",
        "data.json",
        "config.xml",
        "main.py",
        "app.js",
        "main.c",
        "main.cpp",
        "site.css",
    )

    for filename in filenames:
        assert not file_filter.should_ignore(
            Path(filename)
        )