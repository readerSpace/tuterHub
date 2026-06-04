import httpx
from django.conf import settings


class AIServiceError(RuntimeError):
    pass


def _post(path, payload):
    try:
        response = httpx.post(
            f'{settings.AI_SERVICE_URL}{path}',
            json=payload,
            timeout=settings.AI_SERVICE_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise AIServiceError(f'AI service request failed for {path}: {exc}') from exc


def check_ai_service_health():
    try:
        response = httpx.get(
            f'{settings.AI_SERVICE_URL}/health',
            timeout=settings.AI_SERVICE_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise AIServiceError(f'AI service health check failed: {exc}') from exc


def call_ai_lesson_feedback(payload):
    return _post('/ai/lesson-feedback', payload)


def call_ai_homework_suggestion(payload):
    return _post('/ai/homework-suggestion', payload)


def call_ai_study_plan(payload):
    return _post('/ai/study-plan', payload)