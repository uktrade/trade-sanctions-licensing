from core.views.base_views import BaseSaveAndReturnModelFormView
from django.http import HttpResponseRedirect
from django.shortcuts import Http404


class EntityView(BaseSaveAndReturnModelFormView):
    @property
    def pk_url_kwarg(self) -> str:
        raise NotImplementedError("You need to implement the pk_url_kwarg property")

    @property
    def model(self):
        raise NotImplementedError("You need to implement the model property")

    @property
    def object(self):
        pk = self.kwargs[self.pk_url_kwarg]
        child_object = self.model.objects.get(
            pk=pk,
            licence=self.licence_object,
        )
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


class DeleteAnEntityView(EntityView):
    """Base view for deleting an entity from the database. This is used for infinitely looping sub-journeys, such as
    add a business/recipient/individual."""

    allow_zero_entities = False

    def post(self, request, *args, **kwargs):
        entities = self.model.objects.filter(licence=self.licence_object)
        if self.allow_zero_entities or len(entities) > 1:
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404()
