import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: settings.AUTH_USER_MODEL):
    assert user.get_absolute_url() == f"/users/{user.username}/"


def test_user_is_student(user: settings.AUTH_USER_MODEL):
    # by default a user that signs up is not a student or staff
    assert not user.is_student
    assert not user.is_staff
    user.is_student = True
    user.is_staff = True
    assert user.is_student
    assert user.is_staff
