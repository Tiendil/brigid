from fastapi import HTTPException


class PageNotFound(HTTPException):
    def __init__(self, **kwargs) -> None:
        super().__init__(status_code=404, **kwargs)
