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
    path("third-party", views_start.ThirdPartyView.as_view(), name="are_you_third_party"),
    path("your-email-address", views_start.WhatIsYouEmailAddressView.as_view(), name="what_is_your_email"),
    path("enter-security-code", views_start.EmailVerifyView.as_view(), name="email_verify"),
    path("request-new-code", views_start.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("your-details", views_start.YourDetailsView.as_view(), name="your_details"),
]

views_business_urls = [
    path(
        "business-registered-with-companies-house",
        views_business.IsTheBusinessRegisteredWithCompaniesHouseView.as_view(),
        name="is_the_business_registered_with_companies_house",
    ),
    path(
        "registered-company-number",
        views_business.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path(
        "where-business-located/<uuid:business_uuid>",
        views_business.WhereIsTheBusinessLocatedView.as_view(),
        name="where_is_the_business_located",
    ),
    path(
        "check-company-details/<str:business_uuid>",
        views_business.CheckCompanyDetailsView.as_view(),
        name="check_company_details",
    ),
    path(
        "business-location",
        views_business.ManualCompaniesHouseInputView.as_view(),
        name="manual_companies_house_input",
    ),
    path(
        "business-details/<str:location>/<uuid:business_uuid>", views_business.AddABusinessView.as_view(), name="add_a_business"
    ),
    path("delete-business", views_business.DeleteBusinessView.as_view(), name="delete_business"),
    path("add-business", views_business.BusinessAddedView.as_view(), name="business_added"),
]

views_individual_urls = [
    path("individual-details/<str:individual_uuid>", views_individual.AddAnIndividualView.as_view(), name="add_an_individual"),
    path(
        "individuals-home-address/<str:location>/<str:individual_uuid>",
        views_individual.WhatIsIndividualsAddressView.as_view(),
        name="what_is_individuals_address",
    ),
    path("delete-individual", views_individual.DeleteIndividualView.as_view(), name="delete_individual"),
    path("add-individual", views_individual.IndividualAddedView.as_view(), name="individual_added"),
    path(
        "business-details",
        views_individual.BusinessEmployingIndividualView.as_view(),
        name="business_employing_individual",
    ),
]

views_yourself_urls = [
    path("your-name-nationality-location", views_yourself.AddYourselfView.as_view(), name="add_yourself"),
    path(
        "your-home-address/<str:location>",
        views_yourself.AddYourselfAddressView.as_view(),
        name="add_yourself_address",
    ),
    path(
        "check-your-details-add-individuals",
        views_yourself.YourselfAndIndividualAddedView.as_view(),
        name="yourself_and_individual_added",
    ),
    path(
        "delete-individual-from-yourself",
        views_yourself.DeleteIndividualFromYourselfView.as_view(),
        name="delete_individual_from_yourself",
    ),
]

views_existing_licence_urls = [
    path("previous-licence", views_existing_licence.PreviousLicenceView.as_view(), name="previous_licence"),
]

views_services_urls = [
    path("services-type", views_services.TypeOfServiceView.as_view(), name="type_of_service"),
    path(
        "professional-or-business-services",
        views_services.ProfessionalOrBusinessServicesView.as_view(),
        name="professional_or_business_services",
    ),
    path("describe-specific-activities", views_services.ServiceActivitiesView.as_view(), name="service_activities"),
    path("sanctions-regime", views_services.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"),
]

views_recipients_urls = [
    path(
        "recipient-location/<uuid:recipient_uuid>",
        views_recipients.WhereIsTheRecipientLocatedView.as_view(),
        name="where_is_the_recipient_located",
    ),
    path(
        "recipient-location",
        views_recipients.WhereIsTheRecipientLocatedView.as_view(),
        name="where_is_the_recipient_located_no_uuid",
    ),
    path(
        "recipient-details/<str:location>/<uuid:recipient_uuid>",
        views_recipients.AddARecipientView.as_view(),
        name="add_a_recipient",
    ),
    path("delete-recipient", views_recipients.DeleteRecipientView.as_view(), name="delete_recipient"),
    path("add-recipient", views_recipients.RecipientAddedView.as_view(), name="recipient_added"),
    path(
        "provider-recipient-relationship/<str:recipient_uuid>",
        views_recipients.RelationshipProviderRecipientView.as_view(),
        name="relationship_provider_recipient",
    ),
]

views_grounds_purpose_urls = [
    path("licensing-grounds", views_grounds_purpose.LicensingGroundsView.as_view(), name="licensing_grounds"),
    path(
        "other-licensing-grounds",
        views_grounds_purpose.LicensingGroundsLegalAdvisoryView.as_view(),
        name="licensing_grounds_legal_advisory",
    ),
    path("services-purpose", views_grounds_purpose.PurposeOfProvisionView.as_view(), name="purpose_of_provision"),
]

views_documents_urls = [
    path("upload-documents", views_documents.UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete-documents", views_documents.DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download-document/<str:file_name>", views_documents.DownloadDocumentView.as_view(), name="download_document"),
]
views_end_urls = [
    path("check-your-answers", views_end.CheckYourAnswersView.as_view(), name="check_your_answers"),
    path("declaration", views_end.DeclarationView.as_view(), name="declaration"),
    path("application-complete", views_end.CompleteView.as_view(), name="complete"),
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
