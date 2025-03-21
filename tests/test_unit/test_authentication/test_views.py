from unittest.mock import MagicMock, patch

from authentication.utils import TOKEN_SESSION_KEY
from authentication.views import REDIRECT_SESSION_FIELD_NAME
from authlib.jose.errors import InvalidClaimError
from django.urls import reverse


@patch("authentication.views.get_token")
@patch("authentication.views.authenticate")
@patch("authentication.views.settings.GOV_UK_ONE_LOGIN_CONFIG")
def test_correct_authentication_flow(mocked_one_login_config, mocked_authenticate, mocked_get_token, test_apply_user, al_client):
    mocked_one_login_config.return_value = MagicMock(authorise_url="http://test_url")
    response = al_client.get(reverse("authentication:login") + "?next=/test_url")
    state = al_client.session.get(f"{TOKEN_SESSION_KEY}_oauth_state", None)
    assert state

    assert f"{TOKEN_SESSION_KEY}_oauth_nonce" in al_client.session
    assert al_client.session[REDIRECT_SESSION_FIELD_NAME] == "/test_url"

    mocked_get_token.return_value = {"sub": "1234"}
    mocked_authenticate.return_value = test_apply_user
    response = al_client.get(reverse("authentication:callback") + f"?code=1234&state={state}")
    assert response.url == "/test_url"
    assert al_client.session["_auth_user_id"] == str(test_apply_user.pk)


def test_callback_no_code(al_client):
    response = al_client.get("/authentication/callback/?state=1234")
    assert response.url == reverse("authentication:login")


def test_callback_no_state(al_client):
    session = al_client.session
    session[f"{TOKEN_SESSION_KEY}_oauth_state"] = "1234"
    session.save()
    response = al_client.get(reverse("authentication:callback") + "?code=1234")
    assert response.status_code == 400


@patch("authentication.views.get_token")
def test_bad_token(patched_get_token, al_client):
    session = al_client.session
    session[f"{TOKEN_SESSION_KEY}_oauth_state"] = "1234"
    session.save()

    patched_get_token.side_effect = InvalidClaimError(claim="1234")
    response = al_client.get(reverse("authentication:callback") + "?code=1234&state=1234")
    assert response.status_code == 400
