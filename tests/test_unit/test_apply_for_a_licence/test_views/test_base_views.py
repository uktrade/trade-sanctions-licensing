import uuid
from copy import deepcopy

import pytest
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.forms.base_forms import BaseForm
from core.urls import urlpatterns
from django import forms
from django.urls import path, reverse


@pytest.fixture(autouse=True)
def setup_urls():
    # we do the setup for both of these tests here as we can only touch urlpatterns once per file,
    # it's all a bit hacky but coverage is coverage.

    # first cloning the classes to stop it affecting other tests.
    TestAddAnEntityView = deepcopy(AddAnEntityView)
    TestDeleteAnEntityView = deepcopy(DeleteAnEntityView)

    # then set up the clasess with the required attributes

    TestAddAnEntityView.step_name = "add_a_thing"
    TestAddAnEntityView.url_parameter_key = "entity_uuid"
    TestAddAnEntityView.session_key = "entities"
    TestAddAnEntityView.form_class = ThingForm
    TestAddAnEntityView.success_url = "/"

    TestDeleteAnEntityView.step_name = "add_a_thing"
    TestDeleteAnEntityView.url_parameter_key = "entity_uuid"
    TestDeleteAnEntityView.session_key = "entities"
    TestDeleteAnEntityView.form_class = ThingForm
    TestDeleteAnEntityView.success_url = "/"

    # adding the new views to url patterns
    urlpatterns.append(
        path("add_a_thing/<uuid:entity_uuid>", TestAddAnEntityView.as_view(), name="add_a_thing"),
    )
    urlpatterns.append(
        path("delete_a_thing", TestDeleteAnEntityView.as_view(), name="delete_a_thing"),
    )

    yield
    urlpatterns.pop()
    urlpatterns.pop()


class ThingForm(BaseForm):
    name = forms.CharField()


def test_add_a_thing_view(authenticated_al_client):
    thing_1_uuid = uuid.uuid4()
    thing_2_uuid = uuid.uuid4()

    authenticated_al_client.post(reverse("add_a_thing", kwargs={"entity_uuid": thing_1_uuid}), data={"name": "an entity"})

    entities = authenticated_al_client.session["entities"]
    assert len(entities) == 1
    entity_uuid = list(entities.keys())[0]

    assert entities[entity_uuid]["cleaned_data"]["name"] == "an entity"
    assert entities[entity_uuid]["dirty_data"]["name"] == "an entity"

    # test creation
    authenticated_al_client.post(reverse("add_a_thing", kwargs={"entity_uuid": thing_2_uuid}), data={"name": "Another entity"})
    entities = authenticated_al_client.session["entities"]
    assert len(entities) == 2
    entity_uuid = list(entities.keys())[1]
    assert entities[entity_uuid]["cleaned_data"]["name"] == "Another entity"
    assert entities[entity_uuid]["dirty_data"]["name"] == "Another entity"


def test_delete_a_thing_view(authenticated_al_client):
    # adding an entity to the session
    session = authenticated_al_client.session
    entity_uuid = str(uuid.uuid4())
    session["entities"] = {entity_uuid: {"cleaned_data": {"name": "an entity"}, "dirty_data": {"name": "an entity"}}}
    session.save()

    authenticated_al_client.post(reverse("delete_a_thing"), data={"entity_uuid": entity_uuid})

    # shouldn't be deleted as allow_zero_things is False
    entities = authenticated_al_client.session["entities"]
    assert len(entities) == 1

    # now try normal deletion, create 2 entities
    session = authenticated_al_client.session
    entity_uuid = str(uuid.uuid4())
    another_entity_uuid = str(uuid.uuid4())
    session["entities"] = {
        entity_uuid: {"cleaned_data": {"name": "an entity"}, "dirty_data": {"name": "an entity"}},
        another_entity_uuid: {"cleaned_data": {"name": "Another entity"}, "dirty_data": {"name": "Another entity"}},
    }
    session.save()

    authenticated_al_client.post(reverse("delete_a_thing"), data={"entity_uuid": entity_uuid})

    # shouldn't be deleted as allow_zero_things is False
    entities = authenticated_al_client.session["entities"]
    assert len(entities) == 1


def test_delete_a_thing_and_change_success_url_view(authenticated_al_client):
    # adding an entity to the session
    session = authenticated_al_client.session
    entity_uuid = str(uuid.uuid4())
    session["entities"] = {entity_uuid: {"cleaned_data": {"name": "an entity"}, "dirty_data": {"name": "an entity"}}}
    session.save()

    # create 3 entities
    session = authenticated_al_client.session
    entity_uuid = str(uuid.uuid4())
    another_entity_uuid = str(uuid.uuid4())
    third_entity_uuid = str(uuid.uuid4())
    session["entities"] = {
        entity_uuid: {"cleaned_data": {"name": "an entity"}, "dirty_data": {"name": "an entity"}},
        another_entity_uuid: {"cleaned_data": {"name": "Another entity"}, "dirty_data": {"name": "Another entity"}},
        third_entity_uuid: {"cleaned_data": {"name": "Third entity"}, "dirty_data": {"name": "Third entity"}},
    }
    session.save()

    # delete an entity with a different success_url
    response = authenticated_al_client.post(
        reverse("delete_a_thing"), data={"entity_uuid": entity_uuid, "success_url": "check_your_answers"}
    )

    entities = authenticated_al_client.session["entities"]
    assert len(entities) == 2
    assert response.status_code == 302
    assert response.url == reverse("check_your_answers")

    response = authenticated_al_client.post(reverse("delete_a_thing"), data={"entity_uuid": third_entity_uuid})
    entities = authenticated_al_client.session["entities"]

    assert len(entities) == 1
    assert response.status_code == 302
    assert response.url == "/"
