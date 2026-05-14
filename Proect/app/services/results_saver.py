from sqlalchemy.orm import Session
from app import models


def save_attempt(db:Session, user_id: int, score:int, total: int, advice: str):
    attempt = models.TestAttempt(user_id=user_id, score=score, total_questions=total, advice=advice)
    db.add(attempt)
    db.commit()
    return attempt