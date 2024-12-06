# from datetime import timedelta
from unittest.mock import patch

from apply_for_a_licence.models_types import Session, UserEmailVerification
from apply_for_a_licence.views.views_start import EmailVerifyView
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse


class TestEmailVerifyCodeView:
    def test_post(self, al_client):
        request_object = RequestFactory().get("/")

        request_object.session = al_client.session
        session = al_client.session
        user_email_address = "test@testmail.com"
        session["user_email_address"] = user_email_address
        session.save()
        view = EmailVerifyView()
        view.setup(request_object)
        verify_code = "012345"
        user_session = Session.objects.get(session_key=session.session_key)
        UserEmailVerification.objects.create(
            user_session=user_session,
            email_verification_code=verify_code,
        )
        data = {"email_verification_code": verify_code}
        response = view.post(request_object, data)

        # Assert returns success redirect
        expected_response = HttpResponse(status=200, content_type="text/html; charset=utf-8")

        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]

    # TODO: to be updated
    @patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
    def test_ratelimit(self, mocked_is_ratelimited, al_client):
        UserEmailVerification.objects.create(
            user_session=al_client.session._get_session_from_db(), email_verification_code="123456"
        )

        # rate limit response
        response = al_client.post(reverse("email_verify"), data={"email_verification_code": "123456"})
        assert response.status_code == 200
        assert response.wsgi_request.limited is True
        form = response.context["form"]
        assert "email_verification_code" in form.errors
        assert (
            form.errors.as_data()["email_verification_code"][0].message
            == "You've tried to verify your email too many times. Try again in 1 minute"
        )

    # TODO: uncomment and fix test
    # @patch("apply_for_a_licence.views.views_start.verify_email")
    # def test_form_invalid_resent_code(self, mocked_email_verify, al_client):
    #     session = al_client.session
    #     session["user_email_address"] = "test@example.com"
    #     session.save()
    #
    #     verification = UserEmailVerification.objects.create(
    #         user_session=al_client.session._get_session_from_db(), email_verification_code="123456"
    #     )
    #     verification.date_created = verification.date_created - timedelta(minutes=30)
    #     verification.save()
    #
    #     response = al_client.post(reverse("email_verify"), data={"email_verification_code": "123456"})
    #     assert response.status_code == 200
    #     assert mocked_email_verify.called_once
    #     assert mocked_email_verify.called_with("test@example.com")
