from datetime import timedelta

import pytest
from apply_for_a_licence.forms import forms_start as forms
from apply_for_a_licence.models import UserEmailVerification
from django import forms as django_forms
from django.test import RequestFactory


class TestStartForm:
    def test_required(self):
        form = forms.StartForm(data={"who_do_you_want_the_licence_to_cover": None})
        assert not form.is_valid()
        assert "who_do_you_want_the_licence_to_cover" in form.errors
        assert form.errors.as_data()["who_do_you_want_the_licence_to_cover"][0].code == "required"

    def test_widget(self):
        form = forms.StartForm()
        assert isinstance(form.fields["who_do_you_want_the_licence_to_cover"].widget, django_forms.RadioSelect)


class TestThirdPartyForm:
    def test_required(self):
        form = forms.ThirdPartyForm(data={"are_you_applying_on_behalf_of_someone_else": None})
        assert not form.is_valid()
        assert "are_you_applying_on_behalf_of_someone_else" in form.errors
        assert form.errors.as_data()["are_you_applying_on_behalf_of_someone_else"][0].code == "required"


class TestEmailForm:
    def test_required(self):
        form = forms.WhatIsYourEmailForm(data={"email": None})
        assert not form.is_valid()
        assert "email" in form.errors
        assert form.errors.as_data()["email"][0].code == "required"

    def test_invalid(self):
        form = forms.WhatIsYourEmailForm(data={"email": "invalid"})
        assert not form.is_valid()
        assert "email" in form.errors
        assert form.errors.as_data()["email"][0].code == "invalid"


class TestEmailVerifyForm:
    verify_code = "123456"

    @pytest.fixture(autouse=True)
    def user_email_verification_object(self, authenticated_al_client):
        self.obj = UserEmailVerification.objects.create(
            user_session=authenticated_al_client.session._get_session_from_db(),
            email_verification_code=self.verify_code,
        )
        user_request_object = RequestFactory().get("/")
        user_request_object.session = authenticated_al_client.session._get_session_from_db()
        self.request_object = user_request_object

    def test_email_verify_form_correct(self, authenticated_al_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert form.is_valid()

    def test_email_verify_form_incorrect_code(self, authenticated_al_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": "1"}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors

    def test_email_verify_form_expired_code_2_hours(self, authenticated_al_client):
        self.obj.date_created = self.obj.date_created - timedelta(days=1)
        self.obj.save()
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "invalid")

    def test_email_verify_form_expired_code_1_hour(self, authenticated_al_client):
        self.obj.date_created = self.obj.date_created - timedelta(minutes=61)
        self.obj.save()
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "expired")


class TestYourDetailsForm:
    def test_required(self):
        form = forms.YourDetailsForm(data={"applicant_full_name": None})
        assert not form.is_valid()
        assert "applicant_full_name" in form.errors
        assert form.errors.as_data()["applicant_full_name"][0].code == "required"
