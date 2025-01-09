from unittest import mock

from authentication.backends import OneLoginBackend, StaffSSOBackend
from authentication.types import UserInfo
from django.contrib.auth.models import User
from freezegun import freeze_time


class TestOneLoginBackend:
    @freeze_time("2024-01-01 12:00:00")
    @mock.patch.multiple(
        "authentication.backends",
        get_client=mock.DEFAULT,
        get_userinfo=mock.DEFAULT,
        autospec=True,
    )
    def test_user_valid_user_create(self, apply_rf, **mocks):
        mocks["get_userinfo"].return_value = UserInfo(
            sub="some-unique-key", email="user@test.com", email_verified=True  # /PS-IGNORE
        )

        user = OneLoginBackend().authenticate(apply_rf)
        assert user is not None
        assert user.email == "user@test.com"
        assert user.username == "some-unique-key"
        assert user.has_usable_password() is False

    def test_get_or_create_user(self, db):
        profile: UserInfo = {"sub": "some-unique-key", "email": "test@example.com"}
        user = OneLoginBackend().get_or_create_user(profile)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "some-unique-key"

    def test_create_user_that_already_exists(self, db):
        User.objects.create(
            username="some-unique-key",
            email="test@example.com",
        )
        assert User.objects.count() == 1

        profile: UserInfo = {"sub": "some-unique-key", "email": "test@example.com"}
        user = OneLoginBackend().get_or_create_user(profile)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "some-unique-key"
        assert User.objects.count() == 1

    @freeze_time("2024-01-01 12:00:00")
    @mock.patch.multiple(
        "authentication.backends",
        get_client=mock.DEFAULT,
        get_userinfo=mock.DEFAULT,
        autospec=True,
    )
    def test_only_works_with_apply(self, viewer_rf, **mocks):
        mocks["get_userinfo"].return_value = UserInfo(sub="some-unique-key", email="user@test.com")

        user = OneLoginBackend().authenticate(viewer_rf)
        assert user is None


class TestStaffSSOBackend:
    def test_get_or_create_user(self, db):
        profile = {
            "email_user_id": "caseworker",
            "email": "caseworker@example.com",
            "first_name": "Case",
            "last_name": "Worker",
        }
        assert User.objects.count() == 0
        user = StaffSSOBackend().get_or_create_user(profile)
        assert user is not None
        assert user.email == "caseworker@example.com"
        assert user.username == "caseworker"
        assert user.first_name == "Case"
        assert user.last_name == "Worker"
        assert user.has_usable_password() is False
        assert user.is_active is False
        assert user.is_staff is False
        assert User.objects.count() == 1

    def test_only_works_with_view(self, apply_rf):
        user = StaffSSOBackend().authenticate(apply_rf)
        assert user is None
