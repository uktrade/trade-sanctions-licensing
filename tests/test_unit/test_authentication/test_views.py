from django.urls import reverse


def test_redirect_to_login(al_client):
    response = al_client.get(reverse("start"))
    assert reverse("authentication:login") in response.url


def test_use_one_login_for_apply(al_client):
    response = al_client.get(reverse("apply"))
    assert reverse("authentication:login") in response.url
