from authentication.mixins import LoginRequiredMixin


def test_all_views_require_login():
    # gets all views from apply_for_a_licence and asserts that they all require login
    from view_a_licence.urls import urlpatterns

    views = []
    for pattern in urlpatterns:
        if hasattr(pattern.callback, "cls"):
            view = pattern.callback.cls
        elif hasattr(pattern.callback, "view_class"):
            view = pattern.callback.view_class
        else:
            view = pattern.callback
        views.append(view)

    for view in views:
        assert issubclass(view, LoginRequiredMixin)
