from pydantic import BaseModel, HttpUrl
from typing import Dict

class Response(BaseModel):
    url: HttpUrl
    headers: Dict[str, str]
    cookies: Dict[str, str]
    page_source: str