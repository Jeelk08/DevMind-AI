
class AIClientException(Exception):
    """
    Base Exception for all AI client errors.
    """
    pass

class GeminiClientException(Exception):
    """Raised when communication with Gemini fails."""
    pass