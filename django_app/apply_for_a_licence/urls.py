from apply_for_a_licence.views import (
    views_business,
    views_documents,
    views_end,
    views_existing_licence,
    views_grounds_purpose,
    views_individual,
    views_recipients,
    views_services,
    views_start,
    views_yourself,
)
from django.urls import path

views_start_urls = [
    path("", views_start.StartView.as_view(), name="start"),
    path("are_you_third_party", views_start.ThirdPartyView.as_view(), name="are_you_third_party"),
    path("what_is_your_email", views_start.WhatIsYouEmailAddressView.as_view(), name="what_is_your_email"),
    path("email_verify", views_start.EmailVerifyView.as_view(), name="email_verify"),
    path("request_verify_code", views_start.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("your_details", views_start.YourDetailsView.as_view(), name="your_details"),
]

views_business_urls = [
    path(
        "is_the_business_registered_with_companies_house",
        views_business.IsTheBusinessRegisteredWithCompaniesHouseView.as_view(),
        name="is_the_business_registered_with_companies_house",
    ),
    path(
        "do_you_know_the_registered_company_number",
        views_business.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path(
        "where_is_the_business_located",
        views_business.WhereIsTheBusinessLocatedView.as_view(),
        name="where_is_the_business_located",
    ),
    path(
        "check_company_details/<str:business_uuid>",
        views_business.CheckCompanyDetailsView.as_view(),
        name="check_company_details",
    ),
    path(
        "manual_companies_house_input",
        views_business.ManualCompaniesHouseInputView.as_view(),
        name="manual_companies_house_input",
    ),
    path("add_a_business/<str:location>", views_business.AddABusinessView.as_view(), name="add_a_business"),
    path("delete_business", views_business.DeleteBusinessView.as_view(), name="delete_business"),
    path("business_added", views_business.BusinessAddedView.as_view(), name="business_added"),
]

views_individual_urls = [
    path("add_an_individual", views_individual.AddAnIndividualView.as_view(), name="add_an_individual"),
    path(
        "what_is_individuals_address/<str:location>/<str:individual_uuid>",
        views_individual.WhatIsIndividualsAddressView.as_view(),
        name="what_is_individuals_address",
    ),
    path("delete_individual", views_individual.DeleteIndividualView.as_view(), name="delete_individual"),
    path("individual_added", views_individual.IndividualAddedView.as_view(), name="individual_added"),
    path(
        "business_employing_individual",
        views_individual.BusinessEmployingIndividualView.as_view(),
        name="business_employing_individual",
    ),
]

views_yourself_urls = [
    path("add_yourself", views_yourself.AddYourselfView.as_view(), name="add_yourself"),
    path("add_yourself_address", views_yourself.AddYourselfAddressView.as_view(), name="add_yourself_address"),
    path(
        "yourself_and_individual_added",
        views_yourself.YourselfAndIndividualAddedView.as_view(),
        name="yourself_and_individual_added",
    ),
    path(
        "delete_individual_from_yourself",
        views_yourself.DeleteIndividualFromYourselfView.as_view(),
        name="delete_individual_from_yourself",
    ),
]

views_existing_licence_urls = [
    path("previous_licence", views_existing_licence.PreviousLicenceView.as_view(), name="previous_licence"),
]

views_services_urls = [
    path("type_of_service", views_services.TypeOfServiceView.as_view(), name="type_of_service"),
    path(
        "professional_or_business_services",
        views_services.ProfessionalOrBusinessServicesView.as_view(),
        name="professional_or_business_services",
    ),
    path("service_activities", views_services.ServiceActivitiesView.as_view(), name="service_activities"),
    path("which_sanctions_regime", views_services.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"),
]

views_recipients_urls = [
    path(
        "where_is_the_recipient_located",
        views_recipients.WhereIsTheRecipientLocatedView.as_view(),
        name="where_is_the_recipient_located",
    ),
    path("add_a_recipient/<str:location>", views_recipients.AddARecipientView.as_view(), name="add_a_recipient"),
    path("delete_recipient", views_recipients.DeleteRecipientView.as_view(), name="delete_recipient"),
    path("recipient_added", views_recipients.RecipientAddedView.as_view(), name="recipient_added"),
    path(
        "relationship_provider_recipient/<str:recipient_uuid>",
        views_recipients.RelationshipProviderRecipientView.as_view(),
        name="relationship_provider_recipient",
    ),
]

views_grounds_purpose_urls = [
    path("licensing_grounds", views_grounds_purpose.LicensingGroundsView.as_view(), name="licensing_grounds"),
    path(
        "licensing_grounds_legal_advisory",
        views_grounds_purpose.LicensingGroundsLegalAdvisoryView.as_view(),
        name="licensing_grounds_legal_advisory",
    ),
    path("purpose_of_provision", views_grounds_purpose.PurposeOfProvisionView.as_view(), name="purpose_of_provision"),
]

views_documents_urls = [
    path("upload_documents", views_documents.UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete_documents", views_documents.DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download_document/<str:file_name>", views_documents.DownloadDocumentView.as_view(), name="download_document"),
]
views_end_urls = [
    path("check_your_answers", views_end.CheckYourAnswersView.as_view(), name="check_your_answers"),
    path("complete", views_end.CompleteView.as_view(), name="complete"),
]
urlpatterns = (
    views_start_urls
    + views_business_urls
    + views_individual_urls
    + views_yourself_urls
    + views_existing_licence_urls
    + views_services_urls
    + views_recipients_urls
    + views_grounds_purpose_urls
    + views_documents_urls
    + views_end_urls
)

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:
    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
