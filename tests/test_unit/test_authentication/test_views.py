from django.urls import reverse


def test_redirect_to_login(al_client):
    response = al_client.get(reverse("start"))
    assert reverse("authentication:login") in response.url
