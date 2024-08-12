from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View


class ResetSessionView(View):
    """Resets and clears the users session"""

    def get(self, request: HttpRequest) -> HttpResponse:
        request.session.flush()
        return redirect("initial_redirect_view")
