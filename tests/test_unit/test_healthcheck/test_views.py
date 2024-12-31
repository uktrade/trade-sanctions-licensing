from unittest.mock import patch

import pytest
from django.urls import reverse

from tests.helpers import get_response_content


@pytest.fixture(autouse=True)
def setup():
    """Need to fix the Sites context processor as healthcheck views don't have a site."""
    with patch("core.sites.context_processors.sites", return_value={}):
        yield


@patch("healthcheck.checks.s3.boto3")
def test_successful_healthcheck(mock_s3_client, al_client):
    mock_s3_client.head_bucket.return_value = {"test": True}
    response = al_client.get(reverse("healthcheck:healthcheck_ping"))
    content = get_response_content(response)
    assert "OK" in content
    assert response.status_code == 200


@patch("healthcheck.views.db_check", return_value=False)
def test_db_broken_healthcheck(mock_db_check, al_client):
    response = al_client.get(reverse("healthcheck:healthcheck_ping"))
    content = get_response_content(response)
    assert "FAIL" in content
    assert response.status_code == 200
