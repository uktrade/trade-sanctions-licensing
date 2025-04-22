from apply_for_a_licence.models import Individual
from apply_for_a_licence.views.base_views import AddAnEntityView


class BaseIndividualFormView(AddAnEntityView):
    model = Individual
    context_object_name = "individuals"
    redirect_with_query_parameters = True


class TestAddAnEntityView:
    def test_pk_url_kwarg(self, request_object):
        view = BaseIndividualFormView()
        view.setup(request_object)
        assert view.pk_url_kwarg == "individual_id"

    def test_redirect_after_post_on_change(self, request_object):
        request_object.GET = {"change": "yes"}
        view = BaseIndividualFormView()
        view.setup(request_object)
        assert not view.redirect_after_post
