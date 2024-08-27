from typing import Any

from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.exceptions import EmailNotVerifiedException
from apply_for_a_licence.models import (
    Applicant,
    Document,
    Ground,
    Individual,
    Licence,
    Organisation,
    Services,
    UserEmailVerification,
)
from django.http import HttpRequest

from .s3 import store_documents_in_s3


class SaveToDB:
    def __init__(
        self,
        request: HttpRequest,
        licence: Licence,
        applicant: Applicant,
        data: dict[str, Any],
        is_individual: bool,
        is_third_party: bool,
        is_on_companies_house: bool,
    ) -> None:
        self.request = request
        self.email_verification = self._get_user_verification
        self.licence = licence
        self.applicant = applicant
        self.data = data
        self.is_individual = is_individual
        self.is_third_party = is_third_party
        self.is_on_companies_house = is_on_companies_house

    @property
    def _get_user_verification(self) -> UserEmailVerification:
        user_email_verification = UserEmailVerification.objects.filter(user_session=self.request.session.session_key).latest(
            "date_created"
        )

        if not user_email_verification.verified:
            # the user hasn't verified their email address, don't let them submit
            raise EmailNotVerifiedException()
        return user_email_verification

    def save_applicant(self) -> Applicant:
        # sole or named individuals journey
        if self.is_individual:
            if self.data["start"]["who_do_you_want_the_licence_to_cover"] == "individual":
                if self.is_third_party:
                    return self.applicant.create(
                        user_email_address=self.data["what_is_your_email"],
                        user_email_verification=self.email_verification,
                        full_name=self.data["your_details"]["full_name"],
                        business=self.data["your_details"]["business"],
                        role=self.data["your_details"]["role"],
                        type_of_relationship=TypeOfRelationshipChoices.named_individuals,
                        held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                        existing_licences=self.data["previous_licence"]["existing_licences"],
                    )
                return self.applicant.create(
                    user_email_address=self.data["what_is_your_email"],
                    user_email_verification=self.email_verification,
                    full_name=f"{self.data['add_an_individual']['first_name']} {self.data['add_an_individual']['last_name']}",
                    business=self.data["business_employing_individual"]["name"],
                    type_of_relationship=TypeOfRelationshipChoices.named_individuals,
                    held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                    existing_licences=self.data["previous_licence"]["existing_licences"],
                )
            else:
                return self.applicant.create(
                    user_email_address=self.data["what_is_your_email"],
                    user_email_verification=self.email_verification,
                    full_name=f"{self.data['add_yourself']['first_name']} {self.data['add_yourself']['last_name']}",
                    type_of_relationship=(
                        TypeOfRelationshipChoices.sole_individual
                        if self.data["start"]["who_do_you_want_the_licence_to_cover"] == "myself"
                        else TypeOfRelationshipChoices.named_individuals
                    ),
                    held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                    existing_licences=self.data["previous_licence"]["existing_licences"],
                )

        # business journey
        elif self.is_on_companies_house and not self.is_third_party:
            return self.applicant.create(
                user_email_address=self.data["what_is_your_email"],
                user_email_verification=self.email_verification,
                full_name=self.data["do_you_know_the_registered_company_number"]["registered_company_name"],
                type_of_relationship=TypeOfRelationshipChoices.business,
                held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                existing_licences=self.data["previous_licence"]["existing_licences"],
            )
        elif self.is_third_party:
            return self.applicant.create(
                user_email_address=self.data["what_is_your_email"],
                user_email_verification=self.email_verification,
                full_name=self.data["your_details"]["full_name"],
                business=self.data["your_details"]["business"],
                role=self.data["your_details"]["role"],
                type_of_relationship=TypeOfRelationshipChoices.business,
                held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                existing_licences=self.data["previous_licence"]["existing_licences"],
            )
        else:
            if self.data["add_a_business_uk"]:
                business_name = self.data["add_a_business_uk"]["name"]
            else:
                business_name = self.data["add_a_business_non_uk"]["name"]
            return self.applicant.create(
                user_email_address=self.data["what_is_your_email"],
                user_email_verification=self.email_verification,
                full_name=business_name,
                type_of_relationship=TypeOfRelationshipChoices.business,
                held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
                existing_licences=self.data["previous_licence"]["existing_licences"],
            )

    def save_licence(self, applicant: Applicant) -> None:
        ground = None
        if self.data.get("licensing_grounds", ""):
            ground = Ground.objects.create(licensing_grounds=list(self.data["licensing_grounds"]), label="test")

        services = Services.objects.create(
            type_of_service=self.data["type_of_service"]["type_of_service"],
            professional_or_business_service=(
                # TODO: remove test data
                "test"
                if not self.data.get("professional_or_business_service", "")
                else self.data.get("professional_or_business_service", "")
            ),
            service_activities=self.data["service_activities"]["service_activities"],
        )

        sanctions_regimes = []
        if self.data["which_sanctions_regime"]:
            sanctions_regimes = [self.data["which_sanctions_regime"]["which_sanctions_regime"]]

        licence = self.licence.create(
            applicant=applicant,
            ground=ground,
            business_registered_on_companies_house="Yes" if self.is_on_companies_house else "No",
            regimes=sanctions_regimes,
            services=services,
            purpose_of_provision=self.data["purpose_of_provision"]["purpose_of_provision"],
        )
        licence.assign_reference()

        self.licence = licence

    def save_individual(self, individual: Individual) -> None:
        if self.data["start"]["who_do_you_want_the_licence_to_cover"] == "myself":
            if self.data["add_yourself_address_uk"]:
                individual.create(
                    licence=self.licence,
                    first_name=self.data["add_yourself"]["first_name"],
                    last_name=self.data["add_yourself"]["last_name"],
                    nationality_and_location=self.data["add_yourself"]["nationality_and_location"],
                    address_line_1=self.data["add_yourself_address_uk"]["address_line_1"],
                    address_line_2=self.data["add_yourself_address_uk"]["address_line_2"],
                    postcode=self.data["add_yourself_address_uk"]["postcode"],
                    country=self.data["add_yourself_address_uk"]["country"],
                    town_or_city=self.data["add_yourself_address_uk"]["town_or_city"],
                    county=self.data["add_yourself_address/uk"]["country"],
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )
            elif self.data["add_yourself_address_non_uk"]:
                individual.create(
                    licence=self.licence,
                    first_name=self.data["add_yourself"]["first_name"],
                    last_name=self.data["add_yourself"]["last_name"],
                    nationality_and_location=self.data["add_yourself"]["nationality_and_location"],
                    address_line_1=self.data["add_yourself_address_non_uk"]["address_line_1"],
                    address_line_2=self.data["add_yourself_address_non_uk"]["address_line_2"],
                    address_line_3=self.data["add_yourself_address_non_uk"]["address_line_3"],
                    address_line_4=self.data["add_yourself_address_non_uk"]["address_line_4"],
                    country=self.data["add_yourself_address_non_uk"]["country"],
                    town_or_city=self.data["add_yourself_address_non_uk"]["town_or_city"],
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )
        else:
            if "what_is_individuals_address_uk" in self.data:
                # named individual journey
                individual.create(
                    licence=self.licence,
                    first_name=self.data["add_an_individual"]["first_name"],
                    last_name=self.data["add_an_individual"]["last_name"],
                    nationality_and_location=self.data["add_an_individual"]["nationality_and_location"],
                    address_line_1=self.data["what_is_individuals_address_uk"]["address_line_1"],
                    address_line_2=self.data["what_is_individuals_address_uk"]["address_line_2"],
                    country=self.data["what_is_individuals_address_uk"]["country"],
                    town_or_city=self.data["what_is_individuals_address_uk"]["town_or_city"],
                    postcode=self.data["what_is_individuals_address_uk"]["postcode"],
                    county=self.data["what_is_individuals_address_uk"]["county"],
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )
            else:
                individual.create(
                    licence=self.licence,
                    first_name=self.data["add_an_individual"]["first_name"],
                    last_name=self.data["add_an_individual"]["last_name"],
                    nationality_and_location=self.data["add_an_individual"]["nationality_and_location"],
                    address_line_1=self.data["what_is_individuals_address_non_uk"]["address_line_1"],
                    address_line_2=self.data["what_is_individuals_address_non_uk"]["address_line_2"],
                    address_line_3=self.data["what_is_individuals_address_non_uk"]["address_line_3"],
                    address_line_4=self.data["what_is_individuals_address_non_uk"]["address_line_4"],
                    country=self.data["what_is_individuals_address_non_uk"]["country"],
                    town_or_city=self.data["what_is_individuals_address_non_uk"]["town_or_city"],
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )

    def save_business(self, business: Organisation, location="") -> None:
        # named individuals employment details
        if self.is_individual:
            business.create(
                licence=self.licence,
                name=self.data["business_employing_individual"]["name"],
                do_you_know_the_registered_company_number="No",
                address_line_1=self.data["business_employing_individual"]["address_line_1"],
                address_line_2=self.data["business_employing_individual"]["address_line_2"],
                address_line_3=self.data["business_employing_individual"]["address_line_3"],
                address_line_4=self.data["business_employing_individual"]["address_line_4"],
                country=self.data["business_employing_individual"]["country"],
                type_of_relationship=TypeOfRelationshipChoices.named_individuals,
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )

        # business journey company details
        elif self.is_on_companies_house:
            business.create(
                licence=self.licence,
                name=self.data["do_you_know_the_registered_company_number"]["registered_company_name"],
                do_you_know_the_registered_company_number="Yes",
                registered_company_number=self.data["do_you_know_the_registered_company_number"]["registered_company_number"],
                registered_office_address=self.data["do_you_know_the_registered_company_number"]["registered_office_address"],
                type_of_relationship=TypeOfRelationshipChoices.business,
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )
        else:
            if self.data["add_a_business_uk"]:
                business.create(
                    licence=self.licence,
                    do_you_know_the_registered_company_number="No",
                    name=self.data["add_a_business_uk"]["name"],
                    address_line_1=self.data["add_a_business_uk"]["address_line_1"],
                    address_line_2=self.data["add_a_business_uk"]["address_line_2"],
                    country=self.data["add_a_business_uk"]["country"],
                    postcode=self.data["add_a_business_uk"]["postcode"],
                    county=self.data["add_a_business_uk"]["county"],
                    town_or_city=self.data["add_a_business_uk"]["town_or_city"],
                    type_of_relationship=TypeOfRelationshipChoices.business,
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )
            elif self.data["add_a_business_non_uk"]:
                business.create(
                    licence=self.licence,
                    do_you_know_the_registered_company_number="No",
                    name=self.data["add_a_business_non_uk"]["name"],
                    address_line_1=self.data["add_a_business_non_uk"]["address_line_1"],
                    address_line_2=self.data["add_a_business_non_uk"]["address_line_2"],
                    address_line_3=self.data["add_a_business_non_uk"]["address_line_3"],
                    address_line_4=self.data["add_a_business_non_uk"]["address_line_4"],
                    country=self.data["add_a_business_non_uk"]["country"],
                    type_of_relationship=TypeOfRelationshipChoices.business,
                    relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
                )

    def save_recipient(self, recipient: Organisation) -> None:
        if self.data["add_a_recipient_uk"]:
            recipient.create(
                licence=self.licence,
                name=self.data["add_a_recipient_uk"]["name"],
                name_of_person=self.data["add_a_recipient_uk"]["name_of_person"],
                website=self.data["add_a_recipient_uk"]["website"],
                email=self.data["add_a_recipient_uk"]["email"],
                additional_contact_details=self.data["add_a_recipient_uk"]["additional_contact_details"],
                address_line_1=self.data["add_a_recipient_uk"]["address_line_1"],
                address_line_2=self.data["add_a_recipient_uk"]["address_line_2"],
                postcode=self.data["add_a_recipient_uk"]["postcode"],
                country=self.data["add_a_recipient_uk"]["country"],
                town_or_city=self.data["add_a_recipient_uk"]["town_or_city"],
                county=self.data["add_a_recipient_uk"]["county"],
                type_of_relationship=TypeOfRelationshipChoices.recipient,
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )
        elif self.data["add_a_recipient_non_uk"]:
            recipient.create(
                licence=self.licence,
                name=self.data["add_a_recipient_non_uk"]["name"],
                name_of_person=self.data["add_a_recipient_non_uk"]["name_of_person"],
                website=self.data["add_a_recipient_non_uk"]["website"],
                email=self.data["add_a_recipient_non_uk"]["email"],
                additional_contact_details=self.data["add_a_recipient_non_uk"]["additional_contact_details"],
                address_line_1=self.data["add_a_recipient_non_uk"]["address_line_1"],
                address_line_2=self.data["add_a_recipient_non_uk"]["address_line_2"],
                address_line_3=self.data["add_a_recipient_non_uk"]["address_line_3"],
                address_line_4=self.data["add_a_recipient_non_uk"]["address_line_4"],
                country=self.data["add_a_recipient_non_uk"]["country"],
                town_or_city=self.data["add_a_recipient_non_uk"]["town_or_city"],
                type_of_relationship=TypeOfRelationshipChoices.recipient,
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )

    def save_document(self, document_obj: Document) -> None:
        # TODO: need to update this to include the permanent bucket path, see DST-529
        documents = self.data["upload_documents"]["document"]
        for document in documents:
            document_obj.objects.create(
                licence=self.licence,
                file=document,
            )
        store_documents_in_s3(self.request, self.licence.id)
