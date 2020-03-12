from typing import Optional
from dataclasses import dataclass


@dataclass
class ShortenedUrl:
    url_id: Optional[str]
    long_url: str
