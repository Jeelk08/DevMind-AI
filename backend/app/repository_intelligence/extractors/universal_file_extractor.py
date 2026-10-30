"""Lightweight structural extraction for common repository files.

This is a shared extraction layer, not a full compiler/parser.
Unsupported files remain searchable through ordinary text chunking.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileInsights:
    path: str
    file_type: str
    references: list[str] = field(default_factory=list)
    structures: list[str] = field(default_factory=list)


class UniversalFileExtractor:
    """Extract imports, references and structural hints."""

    CODE_IMPORT_PATTERNS = (
        # JavaScript / TypeScript imports
        re.compile(
            r"""^\s*import\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]""",
            re.M,
        ),
        re.compile(
            r"""^\s*export\s+.+?\s+from\s+['"]([^'"]+)['"]""",
            re.M,
        ),
        re.compile(
            r"""\brequire\(\s*['"]([^'"]+)['"]\s*\)"""
        ),
        re.compile(
            r"""\bimport\(\s*['"]([^'"]+)['"]\s*\)"""
        ),

        # Python imports
        re.compile(
            r"^\s*from\s+([\w.]+)\s+import\s+",
            re.M,
        ),
        re.compile(
            r"^\s*import\s+([\w.]+)",
            re.M,
        ),

        # Java package imports
        re.compile(
            r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;",
            re.M,
        ),
    )

    def extract(
        self,
        path: Path,
        content: str,
    ) -> FileInsights:

        suffix = path.suffix.lower()

        result = FileInsights(
            path=str(path),
            file_type=suffix.lstrip(".") or "text",
        )

        if suffix in {
            ".py", ".js", ".jsx", ".ts",
            ".tsx", ".java",
        }:
            for pattern in self.CODE_IMPORT_PATTERNS:
                result.references.extend(
                    pattern.findall(content)
                )

            result.structures.extend(
                self._code_symbols(content, suffix)
            )

        elif suffix in {
            ".c", ".h", ".cc", ".cpp",
            ".cxx", ".hpp", ".hh", ".hxx",
        }:
            result.references.extend(
                re.findall(
                    r'^\s*#\s*include\s*[<"]([^>"]+)[>"]',
                    content,
                    re.M,
                )
            )

            result.structures.extend(
                self._code_symbols(content, suffix)
            )

        elif suffix == ".html":
            result.references.extend(
                re.findall(
                    r"""<(?:script|link|img|iframe)[^>]+?
                    (?:src|href)\s*=\s*['"]([^'"]+)['"]""",
                    content,
                    re.I | re.X,
                )
            )

            result.structures.extend(
                f"HTML element: {tag.lower()}"
                for tag in re.findall(
                    r"<([a-zA-Z][\w:-]*)\b",
                    content,
                )
            )

        elif suffix in {".css", ".scss"}:
            result.references.extend(
                re.findall(
                    r"""@import\s+(?:url\()?\s*
                    ['"]?([^'"\s;)]+)""",
                    content,
                    re.I | re.X,
                )
            )

            result.references.extend(
                re.findall(
                    r"""url\(\s*['"]?([^'"\s)]+)""",
                    content,
                    re.I,
                )
            )

            result.structures.extend(
                f"CSS selector: {selector.strip()}"
                for selector in re.findall(
                    r"([^{}]+)\{",
                    content,
                )
                if selector.strip()
                and not selector.strip().startswith("@")
            )

        elif suffix == ".json":
            try:
                parsed = json.loads(content)

                result.structures.extend(
                    self._json_paths(parsed)
                )

            except (json.JSONDecodeError, TypeError):
                result.structures.append(
                    "JSON-like content (could not parse as valid JSON)"
                )

        elif suffix == ".xml":
            try:
                root = ET.fromstring(content)

                result.structures.extend(
                    f"XML element: {element.tag}"
                    for element in root.iter()
                )

                result.references.extend(
                    value
                    for element in root.iter()
                    for key, value in element.attrib.items()
                    if key.lower() in {
                        "href",
                        "src",
                        "schemalocation",
                    }
                )

            except ET.ParseError:
                result.structures.append(
                    "XML-like content (could not parse as valid XML)"
                )

        # Remove duplicates while preserving order.
        result.references = list(
            dict.fromkeys(
                item.strip()
                for item in result.references
                if item.strip()
            )
        )

        result.structures = list(
            dict.fromkeys(
                item.strip()
                for item in result.structures
                if item.strip()
            )
        )

        return result

    @staticmethod
    def _code_symbols(
        content: str,
        suffix: str,
    ) -> list[str]:

        patterns = [
            re.compile(
                r"^\s*(?:export\s+)?(?:default\s+)?"
                r"(?:async\s+)?function\s+([\w$]+)",
                re.M,
            ),
            re.compile(
                r"^\s*(?:export\s+)?class\s+([\w$]+)",
                re.M,
            ),
        ]

        found = []

        for pattern in patterns:
            found.extend(
                f"Symbol: {name}"
                for name in pattern.findall(content)
            )

        return found

    @staticmethod
    def _json_paths(
        value: object,
        prefix: str = "$",
        depth: int = 0,
    ) -> list[str]:

        if depth > 5:
            return []

        paths = []

        if isinstance(value, dict):
            for key, child in list(value.items())[:100]:
                current = f"{prefix}.{key}"

                paths.append(
                    f"JSON key: {current}"
                )

                paths.extend(
                    UniversalFileExtractor._json_paths(
                        child,
                        current,
                        depth + 1,
                    )
                )

        elif isinstance(value, list):
            for child in value[:20]:
                paths.extend(
                    UniversalFileExtractor._json_paths(
                        child,
                        f"{prefix}[]",
                        depth + 1,
                    )
                )

        return paths