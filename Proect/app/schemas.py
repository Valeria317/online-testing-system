from typing import Optional, Dict, List

from pydantic import BaseModel


class UserCreate(BaseModel):
   username: str
   password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionSchema(BaseModel):
    id: int
    text: str
    options: Dict[str, str]

class TestSubmit(BaseModel):
    answer: Dict[str,str]

class ResultResponse(BaseModel):
    correct_count: int
    total: int
    advice: str
    resources: Optional[List[dict]] = []

class AttemptHistory(BaseModel):
    id: int
    score: int
    total_questions: int
    advice: str
    completed_at: str