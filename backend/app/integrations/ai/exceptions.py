class AIClientException(Exception):
    """Base exception for AI provider errors."""
    pass


class AIRateLimitException(AIClientException):
    """Raised when an AI provider's request quota is exhausted."""
    pass


class GeminiClientException(AIClientException):
    """Raised when communication with Gemini fails."""
    pass