import pytest
from django.conf import settings
from django.test import RequestFactory

from static_page_proxy.users.views import UserRedirectView, UserUpdateView
from proxy.views import file_upload, home, proxy

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def test_get_success_url(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_success_url() == f"/users/{user.username}/"

    def test_get_object(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user


class TestUserRedirectView:
    def test_get_redirect_url(
        self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory
    ):
        view = UserRedirectView()
        request = request_factory.get("/fake-url")
        request.user = user

        view.request = request

        assert view.get_redirect_url() == f"/users/{user.username}/"


class TestCustomViews:
    def test_file_upload(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        # user is not staff so requests for file_upload is redirected
        non_auth_request = request_factory.get("/fake-url")
        non_auth_request.user = user
        non_auth_response = file_upload(non_auth_request)
        assert non_auth_response.status_code == 302

        # user is student but not stadd so request for file_upload is redirected
        student_request = request_factory.get("fake-url")
        user.is_student = True
        student_request.user = user
        student_response = file_upload(student_request)
        assert student_response.status_code == 302

        # user is staff so they have access to file_upload
        staff_request = request_factory.get("fake-url")
        user.is_staff = True
        staff_request.user = user
        staff_response = file_upload(staff_request)
        assert staff_response.status_code == 200

    def test_proxy(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        # user is not staff or student so they will be redirected home
        non_auth_request = request_factory.get("/texts/the_jungle/index.html")
        non_auth_request.user = user
        non_auth_response = proxy(non_auth_request, "/texts/the_jungle/index.html")
        assert non_auth_response.status_code == 302

        # user is student so they will have access to non-home custom urls
        # we assume '/texts/the_jungle/index.html' exists
        student_request = request_factory.get("/texts/the_jungle/index.html")
        user.is_student = True
        student_request.user = user
        student_response = proxy(student_request, "/texts/the_jungle/index.html")
        assert student_response.status_code == 200
        student_content = student_response.content.decode("utf-8")
        assert "The Jungle" in student_content

    def test_home(self, user: settings.AUTH_USER_MODEL, request_factory: RequestFactory):
        # user that is not staff nor student cannot access textbook links
        non_auth_request = request_factory.get("/")
        non_auth_request.user = user
        non_auth_response = home(non_auth_request)
        non_auth_content = non_auth_response.content.decode("utf-8")
        assert "Permission from instructor is required to view the textbooks" in non_auth_content
        assert "/texts/the_jungle/index.html" not in non_auth_content

        # user that is student can access textbook links
        # assume '/texts/the_jungle.index.html' exists
        student_request = request_factory.get("/")
        user.is_student = True
        student_request.user = user
        student_response = home(student_request)
        student_content = student_response.content.decode("utf-8")
        assert "Permission from instructor is required to view the textbooks" not in student_content
        assert "/texts/the_jungle/index.html" in student_content
