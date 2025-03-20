from unittest.mock import MagicMock, patch

from django.test import RequestFactory

from django_app.view_a_licence.views import DownloadPDFView


class TestDownloadPDFView:
    @patch("apply_for_a_licence.models.Licence.objects.get", return_value=MagicMock())
    @patch("core.views.base_views.BaseDownloadPDFView")
    def test_successful_get(self, mock_download, mock_licence):
        test_reference = "DE1234"
        request = RequestFactory().get("?reference=" + test_reference)
        expected_header = "Apply for a licence to provide sanctioned trade services: application submitted "

        view = DownloadPDFView()
        view.reference = test_reference
        view.setup(request)
        response = view.get_context_data()

        assert response["header"] == expected_header
        assert response["reference"] == test_reference
        mock_licence.assert_called_with(reference=test_reference)
