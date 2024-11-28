from feedback.models import FeedbackItem

from tests.test_frontend.conftest import PlaywrightTestBase


class TestCollectFeedback(PlaywrightTestBase):
    """Tests for the feedback collection journey"""

    def test_collect_full_feedback(self):
        assert FeedbackItem.objects.count() == 0

        self.page.goto(self.base_url)
        # clicking the link will open a new tab, so we have to expect it
        with self.page.context.expect_page() as new_page_info:
            self.page.get_by_test_id("collect_feedback_link").click()

            new_page = new_page_info.value
            new_page.get_by_label("Very dissatisfied").check()
            assert new_page.get_by_label("I did not experience any").is_visible()
            new_page.get_by_label("I did not experience any").check()
            new_page.get_by_label("Very satisfied").check()
            assert not new_page.get_by_label("I did not experience any").is_visible()
            new_page.get_by_role("button", name="Submit").click()

        assert FeedbackItem.objects.count() == 1
        feedback_item = FeedbackItem.objects.first()
        assert feedback_item.rating == 5
        assert feedback_item.url == "/apply/"
