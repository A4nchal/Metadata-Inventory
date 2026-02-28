from pydantic import BaseModel, HttpUrl

class Request(BaseModel):
    url: HttpUrl