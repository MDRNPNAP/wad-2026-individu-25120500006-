from pydantic import BaseModel, Field

class SessionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    speaker: str = Field(..., min_length=2, max_length=50)
    capacity: int = Field(..., gt=0)
    is_active: bool = True

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int

    class Config:
        from_attributes = True

class PaginatedSessionResponse(BaseModel):
    data: list[SessionResponse]
    total: int
    page: int
    limit: int