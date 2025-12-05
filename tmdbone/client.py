from typing import Any, Optional

class TMDbException(Exception):
    """Base exception for all tmdbone errors."""
    pass

class TMDbAPIError(TMDbException):
    """
    Raised when the API returns an error status code.
    """
    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response_body = response_body
    
    def __str__(self) -> str:
        base = super().__str__()
        meta = []
        if self.status_code:
            meta.append(f"Status: {self.status_code}")
        if self.url:
            meta.append(f"URL: {self.url}")
        
        if self.response_body and isinstance(self.response_body, str):
            if len(self.response_body) > 200:
                preview = self.response_body[:200].replace('\n', ' ')
                meta.append(f"Body: {preview}...")
            else:
                meta.append(f"Body: {self.response_body}")
        
        if meta:
            return f"{base} ({', '.join(meta)})"
        return base
