import datetime
from time import sleep

from django.conf import settings
from django.urls import reverse
from django.utils import timezone


def test_session_not_expired(authenticated_al_client):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = now_time.isoformat()
    session.save()
    sleep(1)

    response = authenticated_al_client.post(reverse("what_is_your_email"), follow=True, data={"email": "test@example.com"})
    new_updated_activity_time = datetime.datetime.fromisoformat(
        authenticated_al_client.session[settings.SESSION_LAST_ACTIVITY_KEY]
    )

    assert new_updated_activity_time > now_time
    assert response.status_code == 200

    # we want to make sure we're actually being progressed to the next step
    assert response.resolver_match.url_name == "email_verify"


def test_session_expired(authenticated_al_client):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()
    sleep(1)

    response = authenticated_al_client.post(reverse("what_is_your_email"), follow=True)

    # we want to make sure we're actually being progressed to the session expired page
    assert response.resolver_match.url_name == "session_expired"
    assert dict(authenticated_al_client.session) == {}


def test_no_session_key(authenticated_al_client, test_apply_user):
    session = authenticated_al_client.session
    session.pop(settings.SESSION_LAST_ACTIVITY_KEY, None)
    session.save()

    response = authenticated_al_client.post(reverse("what_is_your_email"), follow=True, data={"email": "test@example.com"})
    assert response.resolver_match.url_name == "session_expired"
    assert settings.SESSION_LAST_ACTIVITY_KEY not in authenticated_al_client.session


def test_ping_session_view(authenticated_al_client):
    session = authenticated_al_client.session
    session.clear()
    session.save()

    response = authenticated_al_client.get(reverse("ping_session"))
    assert response.status_code == 200
    assert response.content == b"pong"
    assert authenticated_al_client.session[settings.SESSION_LAST_ACTIVITY_KEY]


def test_expired_session_view(authenticated_al_client):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()

    response = authenticated_al_client.get(reverse("session_expired"))
    assert response.status_code == 200
    assert not dict(authenticated_al_client.session)
