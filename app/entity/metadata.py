from typing import Dict

class Metadata:
    def __init__(self, url: str, headers: Dict, cookies: Dict, page_source: str):
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.page_source = page_source