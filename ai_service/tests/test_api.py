from fastapi.testclient import TestClient
from sqlalchemy import text

from ai_service.app.database import Base, SessionLocal, engine
from ai_service.app.main import app
from ai_service.app.models import AIGenerationLog


def _reset_test_database():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text('DROP TABLE IF EXISTS tutoring_student'))
        connection.execute(
            text(
                '''
                CREATE TABLE tutoring_student (
                    id INTEGER PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    grade VARCHAR(50) NOT NULL,
                    school VARCHAR(255),
                    target_school VARCHAR(255),
                    weak_subjects VARCHAR(255),
                    guardian_contact VARCHAR(255),
                    notes TEXT
                )
                '''
            )
        )
        connection.execute(
            text(
                '''
                INSERT INTO tutoring_student (
                    id, full_name, grade, school, target_school, weak_subjects, guardian_contact, notes
                ) VALUES (
                    1, '山田太郎', '中学2年', '大分中学校', '大分上野丘高校', '一次関数,連立方程式', '090-0000-0000', '復習頻度を上げたい'
                )
                '''
            )
        )
        connection.execute(text('DELETE FROM ai_generation_logs'))


def test_health_endpoint_returns_ok():
    _reset_test_database()
    with TestClient(app) as client:
        response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_students_endpoint_returns_student_rows():
    _reset_test_database()
    with TestClient(app) as client:
        response = client.get('/students')

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]['full_name'] == '山田太郎'


def test_lesson_feedback_logs_generation_result():
    _reset_test_database()
    with TestClient(app) as client:
        response = client.post(
            '/ai/lesson-feedback',
            json={
                'student_name': '山田太郎',
                'subject': '数学',
                'lesson_content': '一次関数のグラフと傾きを学習',
                'understanding_level': 3,
                'teacher_note': '式からグラフを書くところで少し迷っていた',
            },
        )

    assert response.status_code == 200
    assert 'feedback' in response.json()

    with SessionLocal() as session:
        log = session.query(AIGenerationLog).one()

    assert log.student_id == 1
    assert log.feature_type == 'lesson_feedback'
    assert '一次関数のグラフと傾きを学習' in log.prompt


def test_ai_log_summary_and_filtered_logs_endpoints():
    _reset_test_database()
    with TestClient(app) as client:
        client.post(
            '/ai/lesson-feedback',
            json={
                'student_name': '山田太郎',
                'subject': '英語',
                'lesson_content': '長文読解の要点整理',
                'understanding_level': 4,
                'teacher_note': '接続詞の見落としがあった',
            },
        )
        client.post(
            '/ai/homework-suggestion',
            json={
                'student_name': '山田太郎',
                'grade': '中学2年',
                'subject': '数学',
                'weak_points': ['一次関数', '連立方程式'],
                'available_minutes': 30,
            },
        )

        summary_response = client.get('/ai/summary')
        logs_response = client.get('/ai/logs', params={'student_id': 1, 'limit': 5})

    assert summary_response.status_code == 200
    assert summary_response.json() == {
        'total_generations': 2,
        'lesson_feedback_count': 1,
        'homework_suggestion_count': 1,
        'study_plan_count': 0,
    }

    assert logs_response.status_code == 200
    logs = logs_response.json()
    assert len(logs) == 2
    assert all(log['student_id'] == 1 for log in logs)
    assert {log['feature_type'] for log in logs} == {'lesson_feedback', 'homework_suggestion'}