import logging
import json
from textwrap import dedent

from openai import OpenAI

from ..config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


def _should_use_mock():
    return settings.openai_use_mock or not settings.has_real_openai_key


def _call_openai(prompt):
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(model=settings.openai_model, input=prompt)
    return (response.output_text or '').strip()


def _extract_json_payload(response_text):
    start = response_text.find('{')
    end = response_text.rfind('}')
    if start != -1 and end != -1 and end >= start:
        response_text = response_text[start:end + 1]
    return json.loads(response_text)


def _mock_lesson_feedback(data):
    understanding_text = {
        1: '基礎から丁寧な復習が必要な状況です。',
        2: '要点の整理を重ねると安定して理解できそうです。',
        3: '基本事項は理解できており、演習で定着を進める段階です。',
        4: '理解は概ね良好で、応用問題への挑戦が有効です。',
        5: '十分に理解できており、発展内容にも取り組める状態です。',
    }
    return (
        f'本日は{data.subject}で{data.lesson_content}に取り組みました。'
        f'{data.teacher_note}という様子が見られ、'
        f'{understanding_text[data.understanding_level]}'
        '次回は今回の内容を使った演習を重ねて、より自信を持って解けるようにしていきます。'
    )


def _mock_homework_suggestion(data):
    weak_points = data.weak_points or [data.subject]
    per_topic_minutes = max(data.available_minutes // len(weak_points), 10)
    homework = []
    for weak_point in weak_points:
        homework.append(f'{weak_point}を{per_topic_minutes}分復習し、基本問題を5問解く')
    homework.append(f'{data.subject}の計算ミスを防ぐため、見直しを5分行う')
    return homework[: max(3, len(weak_points))]


def _mock_study_plan(data):
    weak_subjects = sorted(data.scores, key=lambda item: item.score / item.max_score)
    plan = []
    for week in range(1, data.weeks + 1):
        focus = weak_subjects[(week - 1) % len(weak_subjects)]
        plan.append(
            {
                'week': week,
                'task': (
                    f"{focus.subject}を中心に{data.target_school}対策を進める週です。"
                    f"基礎確認と演習を行い、弱点単元の復習を重点化します。"
                ),
            }
        )
    return plan


def generate_lesson_feedback(data):
    prompt = dedent(
        f'''
        あなたは学習塾の講師です。
        以下の授業記録をもとに、保護者向けの丁寧なコメントを150文字から220文字程度で作成してください。

        生徒名: {data.student_name}
        科目: {data.subject}
        授業内容: {data.lesson_content}
        理解度: {data.understanding_level}/5
        講師メモ: {data.teacher_note}
        '''
    ).strip()

    feedback = _mock_lesson_feedback(data)
    if not _should_use_mock():
        try:
            feedback = _call_openai(prompt)
        except Exception:
            logger.exception('Falling back to mock lesson feedback because OpenAI-backed generation failed')
            feedback = _mock_lesson_feedback(data)

    return {
        'prompt': prompt,
        'response_text': feedback,
        'payload': feedback,
    }


def generate_homework_suggestion(data):
    prompt = dedent(
        f'''
        あなたは学習塾の講師です。
        次の生徒情報をもとに、{data.available_minutes}分で取り組める宿題案をJSONで返してください。
        形式は {{"homework": ["...", "..."]}} にしてください。

        生徒名: {data.student_name}
        学年: {data.grade}
        科目: {data.subject}
        苦手分野: {', '.join(data.weak_points)}
        '''
    ).strip()

    homework = _mock_homework_suggestion(data)
    response_text = json.dumps({'homework': homework}, ensure_ascii=False)
    if not _should_use_mock():
        try:
            response_text = _call_openai(prompt)
            homework = _extract_json_payload(response_text).get('homework', homework)
        except Exception:
            logger.exception('Falling back to mock homework suggestion because OpenAI-backed generation failed')
            homework = _mock_homework_suggestion(data)
            response_text = json.dumps({'homework': homework}, ensure_ascii=False)

    return {
        'prompt': prompt,
        'response_text': response_text,
        'payload': homework,
    }


def generate_study_plan(data):
    score_lines = '\n'.join(
        f'- {score.subject}: {score.score}/{score.max_score}' for score in data.scores
    )
    prompt = dedent(
        f'''
        あなたは受験指導に強い学習塾講師です。
        次の情報から{data.weeks}週間の学習計画をJSONで返してください。
        形式は {{"plan": [{{"week": 1, "task": "..."}}]}} にしてください。

        生徒名: {data.student_name}
        学年: {data.grade}
        志望校: {data.target_school}
        成績:
        {score_lines}
        '''
    ).strip()

    plan = _mock_study_plan(data)
    response_text = json.dumps({'plan': plan}, ensure_ascii=False)
    if not _should_use_mock():
        try:
            response_text = _call_openai(prompt)
            plan = _extract_json_payload(response_text).get('plan', plan)
        except Exception:
            logger.exception('Falling back to mock study plan because OpenAI-backed generation failed')
            plan = _mock_study_plan(data)
            response_text = json.dumps({'plan': plan}, ensure_ascii=False)

    return {
        'prompt': prompt,
        'response_text': response_text,
        'payload': plan,
    }
