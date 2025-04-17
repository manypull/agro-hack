from pydantic import BaseModel

class AgroRequest(BaseModel):
    message: str


class AgroResponse(BaseModel):
    result: dict