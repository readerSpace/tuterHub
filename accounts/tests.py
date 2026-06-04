import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
def test_superuser_role_is_forced_to_admin():
	user = User.objects.create_superuser(username='admin', email='admin@example.com', password='password123')
	assert user.role == User.Role.ADMIN
