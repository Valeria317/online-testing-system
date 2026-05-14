from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app import models

TEST_DURATION_MINUTES = 20

def start_new_session(db: Session, user_id: int):
    # удаляем старую незавершенную сессию
    existing = db.query(models.ActiveTestSession).filter(
        models.ActiveTestSession.user_id == user_id,
        models.ActiveTestSession.is_completed == False
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
    
    # используем UTC с часовым поясом
    new_session = models.ActiveTestSession(
        user_id=user_id, 
        started_at=datetime.now(timezone.utc)
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def is_session_valid(db: Session, user_id: int) -> bool:
    session = db.query(models.ActiveTestSession).filter(
        models.ActiveTestSession.user_id == user_id,
        models.ActiveTestSession.is_completed == False
    ).first()
    
    if not session:
        return False
    
    # Приводим started_at к часовому поясу, если он наивный
    started = session.started_at
    if started.tzinfo is None:
        # Если в БД сохранилось без часового пояса, считаем, что это UTC
        started = started.replace(tzinfo=timezone.utc)
    
    elapsed = datetime.now(timezone.utc) - started
    
    if elapsed > timedelta(minutes=TEST_DURATION_MINUTES):
        session.is_completed = True
        db.commit()
        return False
    return True

def get_session_start_time(db: Session, user_id: int):
    session = db.query(models.ActiveTestSession).filter(
        models.ActiveTestSession.user_id == user_id,
        models.ActiveTestSession.is_completed == False
    ).first()
    return session.started_at if session else None

def complete_session(db: Session, user_id: int):
    session = db.query(models.ActiveTestSession).filter(
        models.ActiveTestSession.user_id == user_id,
        models.ActiveTestSession.is_completed == False
    ).first()
    if session:
        session.is_completed = True
        db.commit()
