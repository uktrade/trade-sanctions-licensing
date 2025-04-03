from core.views.base_views import BaseSaveAndReturnModelFormView
from django.http import HttpResponseRedirect
from django.shortcuts import Http404


class EntityView(BaseSaveAndReturnModelFormView):
    @property
    def pk_url_kwarg(self) -> str:
        if self.model:
            return f"{self.model.__name__.lower()}_id"
        else:
            raise NotImplementedError("You need to implement the model property")

    @property
    def model(self):
        raise NotImplementedError("You need to implement the model property")

    @property
    def object(self):
        pk = int(self.kwargs[self.pk_url_kwarg])

        try:
            child_object = self.model.objects.get(
                pk=pk,
                licence=self.licence_object,
            )
        except self.model.DoesNotExist:
            raise Http404()
        return child_object


class AddAnEntityView(EntityView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def save_form(self, form):
        instance = form.save(commit=False)
        instance.licence = self.licence_object
        instance.save()
        return instance

    @property
    def redirect_after_post(self) -> bool:
        # if ?change is yes, then we want to redirect them to the next step, except for when we're not redirecting
        # them with query parameters, because in that case we've said to ourselves that we're not going to redirect
        if self.request.GET.get("change") == "yes" and self.redirect_with_query_parameters:
            # if we are creating a new one, then we want to take them to the next step
            return False
        else:
            return True


class DeleteAnEntityView(EntityView):
    """Base view for deleting an entity from the database. This is used for infinitely looping sub-journeys, such as
    add a business/recipient/individual."""

    allow_zero_entities = False

    def post(self, request, *args, **kwargs):
        entities = self.model.objects.filter(licence=self.licence_object)
        if self.allow_zero_entities or len(entities) > 1:
            self.object.delete()
            return HttpResponseRedirect(self.get_next_url())
        else:
            raise Http404()
