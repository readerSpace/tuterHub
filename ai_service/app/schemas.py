from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class StudentSummary(BaseModel):
    id: int
    full_name: str
    grade: str
    school: str | None = None
    target_school: str | None = None
    weak_subjects: str | None = None
    guardian_contact: str | None = None
    notes: str | None = None


class LessonFeedbackRequest(BaseModel):
    student_name: str
    subject: str
    lesson_content: str
    understanding_level: int = Field(ge=1, le=5)
    teacher_note: str


class LessonFeedbackResponse(BaseModel):
    feedback: str


class HomeworkSuggestionRequest(BaseModel):
    student_name: str
    grade: str
    subject: str
    weak_points: list[str]
    available_minutes: int = Field(gt=0, le=300)


class HomeworkSuggestionResponse(BaseModel):
    homework: list[str]


class ScoreInput(BaseModel):
    subject: str
    score: int = Field(ge=0)
    max_score: int = Field(gt=0)


class StudyPlanRequest(BaseModel):
    student_name: str
    grade: str
    target_school: str
    scores: list[ScoreInput]
    weeks: int = Field(gt=0, le=12)


class StudyPlanItem(BaseModel):
    week: int
    task: str


class StudyPlanResponse(BaseModel):
    plan: list[StudyPlanItem]


class AIGenerationLogSummary(BaseModel):
    total_generations: int
    lesson_feedback_count: int
    homework_suggestion_count: int
    study_plan_count: int


class AIGenerationLogItem(BaseModel):
    id: int
    student_id: int | None = None
    feature_type: str
    prompt: str
    response: str
    created_at: datetime
