from django.urls import path

from . import views

urlpatterns = [
    path("", views.StartView.as_view(), name="start"),
    path("are_you_third_party", views.ThirdPartyView.as_view(), name="are_you_third_party"),
    path("what_is_your_email", views.WhatIsYouEmailAddressView.as_view(), name="what_is_your_email"),
    path("email_verify", views.EmailVerifyView.as_view(), name="email_verify"),
    path("request_verify_code", views.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("previous_licence", views.PreviousLicenceView.as_view(), name="previous_licence"),
    path("your_details", views.YourDetailsView.as_view(), name="your_details"),
    path("add_a_business", views.AddABusinessView.as_view(), name="add_a_business"),
    path("zero_businesses", views.ZeroBusinessesView.as_view(), name="zero_businesses"),
    path("delete_business", views.DeleteBusinessView.as_view(), name="delete_business"),
    path("business_added", views.BusinessAddedView.as_view(), name="business_added"),
    path("add_an_individual", views.AddAnIndividualView.as_view(), name="add_an_individual"),
    path("zero_individuals", views.ZeroIndividualsView.as_view(), name="zero_individuals"),
    path("delete_individual", views.DeleteIndividualView.as_view(), name="delete_individual"),
    path("individual_added", views.IndividualAddedView.as_view(), name="individual_added"),
    path("add_yourself", views.AddYourselfView.as_view(), name="add_yourself"),
    path("add_yourself_address", views.AddYourselfAddressView.as_view(), name="add_yourself_address"),
    path("yourself_and_individual_added", views.YourselfAndIndividualAddedView.as_view(), name="yourself_and_individual_added"),
    path(
        "delete_individual_from_yourself",
        views.DeleteIndividualFromYourselfView.as_view(),
        name="delete_individual_from_yourself",
    ),
    path("complete", views.CompleteView.as_view(), name="complete"),
]
