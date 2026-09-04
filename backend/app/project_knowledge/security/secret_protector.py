import re
from pathlib import Path


class SecretProtector:
    """
    Detects and protects high-confidence secrets before repository
    content reaches chunking, embedding, or persistent indexing.
    """

    SENSITIVE_FILE_PATTERNS = (
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "credentials.*",
        "secrets.*",
    )

    SECRET_PATTERNS = (
        # Google / Gemini API keys
        re.compile(
            r'(?i)(GOOGLE_API_KEY|GEMINI_API_KEY)\s*=\s*["\']([^"\']+)["\']'
        ),

        # Generic API keys
        re.compile(
            r'(?i)(API_KEY|APIKEY)\s*=\s*["\']([^"\']+)["\']'
        ),

        # Passwords
        re.compile(
            r'(?i)(PASSWORD|PASSWD|DB_PASSWORD|DATABASE_PASSWORD)'
            r'\s*=\s*["\']([^"\']+)["\']'
        ),

        # Access / authentication tokens
        re.compile(
            r'(?i)(ACCESS_TOKEN|AUTH_TOKEN|BEARER_TOKEN|TOKEN)'
            r'\s*=\s*["\']([^"\']+)["\']'
        ),

        # Common secret assignments
        re.compile(
            r'(?i)(SECRET|SECRET_KEY)'
            r'\s*=\s*["\']([^"\']+)["\']'
        ),
    )

    REDACTED_VALUE = "[REDACTED]"

    def should_exclude_file(self, path: Path) -> bool:
        """
        Returns True when the entire file should be excluded from
        repository knowledge.
        """

        name = path.name

        for pattern in self.SENSITIVE_FILE_PATTERNS:
            if pattern == name:
                return True

            if pattern.startswith("*.") and name.endswith(
                pattern[1:]
            ):
                return True

            if pattern.endswith(".*"):
                prefix = pattern[:-2]

                if name.startswith(prefix):
                    return True

        return False

    def sanitize(self, content: str) -> str:
        """
        Redacts detected secret values while preserving the surrounding
        source-code structure.
        """

        sanitized = content

        for pattern in self.SECRET_PATTERNS:
            sanitized = pattern.sub(
                lambda match: (
                    f'{match.group(1)} = "{self.REDACTED_VALUE}"'
                ),
                sanitized,
            )

        return sanitized