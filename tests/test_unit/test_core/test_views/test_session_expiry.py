import datetime
from time import sleep

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from tests.factories import LicenceFactory


def test_session_not_expired(authenticated_al_client, test_apply_user):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = now_time.isoformat()
    session["licence_id"] = LicenceFactory(user=test_apply_user, who_do_you_want_the_licence_to_cover="individual").id
    session.save()
    sleep(1)

    response = authenticated_al_client.post(
        reverse("your_details"),
        follow=True,
        data={"applicant_full_name": "John Smith", "applicant_business": "business", "applicant_role": "role"},
    )
    new_updated_activity_time = datetime.datetime.fromisoformat(
        authenticated_al_client.session[settings.SESSION_LAST_ACTIVITY_KEY]
    )

    assert new_updated_activity_time > now_time
    assert response.status_code == 200

    # we want to make sure we're actually being progressed to the next step
    assert response.resolver_match.url_name == "tasklist"


def test_session_expired(authenticated_al_client):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()
    sleep(1)

    response = authenticated_al_client.post(reverse("your_details"), follow=True)

    assert response.status_code == 404
    assert dict(authenticated_al_client.session) == {}


def test_ping_session_view(authenticated_al_client):
    session = authenticated_al_client.session
    session.clear()
    session.save()

    response = authenticated_al_client.get(reverse("ping_session"))
    assert response.status_code == 200
    assert response.content == b"pong"
    assert authenticated_al_client.session[settings.SESSION_LAST_ACTIVITY_KEY]


def test_logout_view_expires_session(authenticated_al_client):
    session = authenticated_al_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()

    response = authenticated_al_client.get(reverse("authentication:logout"))
    assert response.status_code == 302
    assert response.resolver_match.url_name == "logout"
    assert not dict(authenticated_al_client.session)


def test_logout_view_with_oidc_token_expires_session(authenticated_al_client):
    session = authenticated_al_client.session
    one_login_token = {"id_token": "fake_token"}
    session["_one_login_token"] = one_login_token
    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()

    response = authenticated_al_client.get(reverse("authentication:logout"))
    assert response.status_code == 302
    assert "oidc.integration.account.gov.uk/logout" in response.url
    assert "post_logout_redirect_uri" in response.url
    assert "authentication/session-expired" in response.url
    assert "id_token_hint=fake_token" in response.url
    assert response.resolver_match.url_name == "logout"
    assert not dict(authenticated_al_client.session)
