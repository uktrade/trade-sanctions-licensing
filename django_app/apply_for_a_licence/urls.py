from django.urls import path

from . import views

urlpatterns = [
    path("", views.StartView.as_view(), name="start"),
    path("are_you_third_party", views.ThirdPartyView.as_view(), name="are_you_third_party"),
    path("what_is_your_email", views.WhatIsYouEmailAddressView.as_view(), name="what_is_your_email"),
    path("your_details", views.YourDetailsView.as_view(), name="your_details"),
    path("email_verify", views.EmailVerifyView.as_view(), name="email_verify"),
    path("request_verify_code", views.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("add_a_business", views.AddABusinessView.as_view(), name="add_a_business"),
    path("add_an_individual", views.AddAnIndividualView.as_view(), name="add_an_individual"),
    path("zero_individuals", views.ZeroIndividualsView.as_view(), name="zero_individuals"),
    path("individual_added", views.IndividualAddedView.as_view(), name="individual_added"),
    path("complete", views.CompleteView.as_view(), name="complete"),
]
