from unittest.mock import mock_open, patch

from core.templatetags.get_css_rules_as_string import get_css_rules_as_string


class TestGetCssRulesAsString:
    @patch("core.templatetags.get_css_rules_as_string.open", new_callable=mock_open, read_data="body { color: red;}")
    @patch("core.templatetags.get_css_rules_as_string.os.path.join", return_value="/test_style.css")
    def test_get_css_rules_as_string(self, mock_path_join, mocked_file_open):
        css_string = get_css_rules_as_string("test_style.css")

        assert css_string == "body { color: red;}"
        mock_path_join.assert_called_once()
        mocked_file_open.assert_called_once_with("/test_style.css", "r", encoding="utf-8")
