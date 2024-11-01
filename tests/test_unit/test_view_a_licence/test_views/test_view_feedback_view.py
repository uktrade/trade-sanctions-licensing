import datetime

from django.urls import reverse

from tests.factories import FeedbackFactory


class TestViewFeedbackView:
    def test_get_queryset(self, vl_client_logged_in):
        FeedbackFactory.create_batch(3)
        response = vl_client_logged_in.get(reverse("view_a_licence:view_feedback"))
        objects = response.context["object_list"]
        assert objects.count() == 3

    def test_get_queryset_with_get_parameters(self, vl_client_logged_in):
        feedback_items = FeedbackFactory.create_batch(3)
        feedback_items[0].created_at = datetime.datetime.now()
        feedback_items[1].created_at = datetime.datetime.now() - datetime.timedelta(days=5)
        feedback_items[2].created_at = datetime.datetime.now() - datetime.timedelta(days=10)
        feedback_items[0].save()
        feedback_items[1].save()
        feedback_items[2].save()

        # date_max query parameter
        query_params = {"date_max": datetime.datetime.now().date() - datetime.timedelta(days=1)}

        response = vl_client_logged_in.get(reverse("view_a_licence:view_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 2
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id not in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id in object_ids

        # date_min query parameter
        query_params = {"date_min": datetime.datetime.now().date() - datetime.timedelta(days=5)}

        response = vl_client_logged_in.get(reverse("view_a_licence:view_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 2
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id not in object_ids

        # date_max and date_min query parameters

        query_params = {
            "date_max": datetime.datetime.now().date() - datetime.timedelta(days=1),
            "date_min": datetime.datetime.now().date() - datetime.timedelta(days=6),
        }

        response = vl_client_logged_in.get(reverse("view_a_licence:view_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 1
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id not in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id not in object_ids
