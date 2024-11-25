from django.urls import reverse
from feedback.models import FeedbackItem

from tests.test_frontend.conftest import PlaywrightTestBase


class TestCollectFeedback(PlaywrightTestBase):
    """Tests for the feedback collection journey"""

    def test_collect_full_feedback(self):
        assert FeedbackItem.objects.count() == 0

        self.page.goto(self.base_url + reverse("feedback:collect_full_feedback"))
        self.page.get_by_label("Very dissatisfied").check()
        assert self.page.get_by_label("I did not experience any").is_visible()
        self.page.get_by_label("I did not experience any").check()
        self.page.get_by_label("Very satisfied").check()
        assert not self.page.get_by_label("I did not experience any").is_visible()
        self.page.get_by_role("button", name="Submit").click()

        assert FeedbackItem.objects.count() == 1
        feedback_item = FeedbackItem.objects.first()
        assert feedback_item.rating == 5
