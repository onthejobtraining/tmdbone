from typing import Optional

class TMDbImageHelper:
    """Helper class to construct full image URLs from TMDb partial paths."""
    BASE_URL = "https://image.tmdb.org/t/p/"

    @classmethod
    def url(cls, path: Optional[str], size: str = "original") -> str:
        """
        Constructs a full image URL. Returns empty string if path is None/Empty.
        
        Args:
            path: The partial path returned by API (e.g. "/abc.jpg")
            size: TMDb size constant (e.g. "w500", "original")
        """
        if not path:
            return ""
        clean_path = path.lstrip('/')
        return f"{cls.BASE_URL}{size}/{clean_path}"
