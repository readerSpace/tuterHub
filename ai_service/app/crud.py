from sqlalchemy import func, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from .models import AIGenerationLog


def list_students(db: Session, limit=100):
    try:
        rows = db.execute(
            text(
                """
                SELECT id, full_name, grade, school, target_school, weak_subjects, guardian_contact, notes
                FROM tutoring_student
                ORDER BY full_name
                LIMIT :limit
                """
            ),
            {'limit': limit},
        ).mappings()
        return [dict(row) for row in rows]
    except (OperationalError, ProgrammingError):
        return []


def find_student_id_by_name(db: Session, student_name: str):
    try:
        return db.execute(
            text(
                """
                SELECT id
                FROM tutoring_student
                WHERE full_name = :student_name
                ORDER BY id
                LIMIT 1
                """
            ),
            {'student_name': student_name},
        ).scalar_one_or_none()
    except (OperationalError, ProgrammingError):
        return None


def create_ai_generation_log(db: Session, student_id, feature_type, prompt, response):
    log = AIGenerationLog(
        student_id=student_id,
        feature_type=feature_type,
        prompt=prompt,
        response=response,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_ai_generation_logs(db: Session, student_id: int | None = None, limit: int = 20):
    query = db.query(AIGenerationLog)
    if student_id is not None:
        query = query.filter(AIGenerationLog.student_id == student_id)

    return query.order_by(AIGenerationLog.created_at.desc(), AIGenerationLog.id.desc()).limit(limit).all()


def get_ai_generation_summary(db: Session):
    rows = db.query(AIGenerationLog.feature_type, func.count(AIGenerationLog.id)).group_by(AIGenerationLog.feature_type).all()
    counts = {feature_type: count for feature_type, count in rows}

    return {
        'total_generations': sum(counts.values()),
        'lesson_feedback_count': counts.get('lesson_feedback', 0),
        'homework_suggestion_count': counts.get('homework_suggestion', 0),
        'study_plan_count': counts.get('study_plan', 0),
    }
