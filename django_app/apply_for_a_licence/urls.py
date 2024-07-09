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
    path(
        "is_the_business_registered_with_companies_house",
        views.IsTheBusinessRegisteredWithCompaniesHouseView.as_view(),
        name="is_the_business_registered_with_companies_house",
    ),
    path(
        "do_you_know_the_registered_company_number",
        views.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path("where_is_the_business_located", views.WhereIsTheBusinessLocatedView.as_view(), name="where_is_the_business_located"),
    path("check_company_details(?P<business_uuid>)", views.CheckCompanyDetailsView.as_view(), name="check_company_details"),
    path("manual_companies_house_input", views.ManualCompaniesHouseInputView.as_view(), name="manual_companies_house_input"),
    path("add_a_business/(?P<location>)", views.AddABusinessView.as_view(), name="add_a_business"),
    path("delete_business", views.DeleteBusinessView.as_view(), name="delete_business"),
    path("business_added", views.BusinessAddedView.as_view(), name="business_added"),
    path("add_an_individual", views.AddAnIndividualView.as_view(), name="add_an_individual"),
    path("delete_individual", views.DeleteIndividualView.as_view(), name="delete_individual"),
    path("individual_added", views.IndividualAddedView.as_view(), name="individual_added"),
    path("business_employing_individual", views.BusinessEmployingIndividualView.as_view(), name="business_employing_individual"),
    path("add_yourself", views.AddYourselfView.as_view(), name="add_yourself"),
    path("add_yourself_address", views.AddYourselfAddressView.as_view(), name="add_yourself_address"),
    path("yourself_and_individual_added", views.YourselfAndIndividualAddedView.as_view(), name="yourself_and_individual_added"),
    path(
        "delete_individual_from_yourself",
        views.DeleteIndividualFromYourselfView.as_view(),
        name="delete_individual_from_yourself",
    ),
    path("type_of_service", views.CompleteView.as_view(), name="type_of_service"),
    path("complete", views.CompleteView.as_view(), name="complete"),
]
