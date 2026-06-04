import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import (
    AIGenerationLogItem,
    AIGenerationLogSummary,
    HomeworkSuggestionRequest,
    HomeworkSuggestionResponse,
    LessonFeedbackRequest,
    LessonFeedbackResponse,
    StudyPlanRequest,
    StudyPlanResponse,
)
from ..services import openai_service


router = APIRouter()


@router.get('/summary', response_model=AIGenerationLogSummary)
def generation_summary(db: Session = Depends(get_db)):
    return crud.get_ai_generation_summary(db)


@router.get('/logs', response_model=list[AIGenerationLogItem])
def generation_logs(
    student_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.list_ai_generation_logs(db, student_id=student_id, limit=limit)


@router.post('/lesson-feedback', response_model=LessonFeedbackResponse)
def lesson_feedback(request: LessonFeedbackRequest, db: Session = Depends(get_db)):
    result = openai_service.generate_lesson_feedback(request)
    crud.create_ai_generation_log(
        db,
        student_id=crud.find_student_id_by_name(db, request.student_name),
        feature_type='lesson_feedback',
        prompt=result['prompt'],
        response=result['response_text'],
    )
    return {'feedback': result['payload']}


@router.post('/homework-suggestion', response_model=HomeworkSuggestionResponse)
def homework_suggestion(request: HomeworkSuggestionRequest, db: Session = Depends(get_db)):
    result = openai_service.generate_homework_suggestion(request)
    crud.create_ai_generation_log(
        db,
        student_id=crud.find_student_id_by_name(db, request.student_name),
        feature_type='homework_suggestion',
        prompt=result['prompt'],
        response=result['response_text'],
    )
    return {'homework': result['payload']}


@router.post('/study-plan', response_model=StudyPlanResponse)
def study_plan(request: StudyPlanRequest, db: Session = Depends(get_db)):
    result = openai_service.generate_study_plan(request)
    crud.create_ai_generation_log(
        db,
        student_id=crud.find_student_id_by_name(db, request.student_name),
        feature_type='study_plan',
        prompt=result['prompt'],
        response=json.dumps(result['payload'], ensure_ascii=False),
    )
    return {'plan': result['payload']}
