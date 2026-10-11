from pydantic import BaseModel

class JWT(BaseModel):
    access_token: str
    token_type: str
