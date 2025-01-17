from transitions import Machine


class StartJourneyMachine(object):
    states = [
        "start",
        "are_you_third_party",
        "what_is_your_email",
        "email_verify",
        "request_verify_code",
        "your_details",
    ]

    def __init__(self, licence_object):
        self.licence_object = licence_object
        transitions = [
            {
                "trigger": "start_chosen",
                "source": "start",
                "dest": "are_you_third_party",
                "conditions": "is_business_or_individual",
            },
            {"trigger": "start_chosen", "source": "start", "dest": "what_is_your_email", "unless": "is_business_or_individual"},
            {"trigger": "what_is_your_email_chosen", "source": "what_is_your_email", "dest": "email_verify"},
            {"trigger": "request_verify_code_chosen", "source": "what_is_your_email", "dest": "request_verify_code"},
            {
                "trigger": "request_verify_code_chosen",
                "source": "request_verify_code",
                "dest": "email_verify",
            },
            {"trigger": "email_verify_chosen", "source": "email_verify", "dest": "your_details", "conditions": "is_third_party"},
            {"trigger": "companies_house_chosen", "source": "companies_house", "dest": "end"},
        ]

        # Initialize the state machine
        self.machine = Machine(model=self, states=StartJourneyMachine.states, initial="start", transitions=transitions)

    def is_business_or_individual(self) -> bool:
        answer = self.licence_object.who_do_you_want_the_licence_to_cover
        if answer in ["business", "individual"]:
            return True
        else:
            return False

    def is_third_party(self) -> bool:
        return self.licence_object.is_third_party


class BusinessJourneyMachine(object):

    # Define some states.
    states = [
        "is_the_business_registered_with_companies_house",
        "do_you_know_the_registered_company_number",
        "where_is_the_business_located",
        "check_company_details",
        "manual_companies_house_input",
        "add_a_business",
        "delete_business",
        "business_added",
    ]

    def __init__(self, licence_object, organisation):
        self.licence_object = licence_object
        self.organisation = organisation

        transitions = [
            {
                "trigger": "is_the_business_registered_with_companies_house_chosen",
                "source": "is_the_business_registered_with_companies_house",
                "dest": "do_you_know_the_registered_company_number",
                "conditions": "is_the_business_registered_with_companies_house",
            },
            {
                "trigger": "is_the_business_registered_with_companies_house_chosen",
                "source": "is_the_business_registered_with_companies_house",
                "dest": "where_is_the_business_located",
                "unless": "is_the_business_registered_with_companies_house",
            },
            {
                "trigger": "do_you_know_the_registered_company_number_chosen",
                "source": "do_you_know_the_registered_company_number",
                "dest": "manual_companies_house_input",
                "conditions": "companies_house_error",
            },
            {
                "trigger": "do_you_know_the_registered_company_number_chosen",
                "source": "do_you_know_the_registered_company_number",
                "dest": "where_is_the_business_located",
                "unless": ["do_you_know_the_registered_company_number", "companies_house_error"],
            },
            {
                "trigger": "do_you_know_the_registered_company_number_chosen",
                "source": "do_you_know_the_registered_company_number",
                "dest": "check_company_details",
                "conditions": "do_you_know_the_registered_company_number",
            },
            {
                "trigger": "where_is_the_business_located_chosen",
                "source": "where_is_the_business_located",
                "dest": "add_a_business",
            },
            {"trigger": "add_a_business_chosen", "source": "add_a_business", "dest": "business_added"},
            {"trigger": "check_company_details_chosen", "source": "check_company_details", "dest": "business_added"},
        ]

        # Initialize the state machine
        self.machine = Machine(
            model=self,
            states=BusinessJourneyMachine.states,
            initial="is_the_business_registered_with_companies_house",
            transitions=transitions,
        )

    def is_the_business_registered_with_companies_house(self) -> bool:
        answer = self.licence_object.business_registered_on_companies_house
        print(answer)
        if answer == "Yes":
            return True
        else:
            return False

    def do_you_know_the_registered_company_number(self):
        answer = self.organisation.do_you_know_the_registered_company_number
        if answer == "Yes":
            return True
        else:
            return False

    def companies_house_error(self) -> bool:
        # if self.request.session.pop("company_details_500", None):
        #     return True
        # else:
        #     return False
        return False


class IndividualJourneyMachine(object):
    pass


class MyselfJourneyMachine(object):
    pass


class ServicesJourneyMachine(object):
    states = [
        "previous_licence",
        "type_of_service",
        "professional_or_business_service",
        "service_activities",
        "which_sanctions_regimes",
        "where_is_the_recipient_located",
        "where_is_the_recipient_located_no_uuid",
        "add_a_recipient",
        "delete_recipient",
        "recipient_added",
        "relationship_provider_recipient",
        "licensing_grounds",
        "licensing_grounds_legal_advisory",
        "purpose_of_provision",
        "upload_documents",
        "delete_documents",
        "check_your_answers",
        "declaration",
        "complete",
    ]

    def __init__(self, licence_object):
        self.licence_object = licence_object
        transitions = [
            {
                "trigger": "start_chosen",
                "source": "start",
                "dest": "are_you_third_party",
                "conditions": "is_business_or_individual",
            },
            {"trigger": "start_chosen", "source": "start", "dest": "what_is_your_email", "unless": "is_business_or_individual"},
            {"trigger": "what_is_your_email_chosen", "source": "what_is_your_email", "dest": "email_verify"},
            {"trigger": "request_verify_code_chosen", "source": "what_is_your_email", "dest": "request_verify_code"},
            {
                "trigger": "request_verify_code_chosen",
                "source": "request_verify_code",
                "dest": "email_verify",
            },
            {"trigger": "email_verify_chosen", "source": "email_verify", "dest": "your_details", "conditions": "is_third_party"},
            {"trigger": "companies_house_chosen", "source": "companies_house", "dest": "end"},
        ]

        # Initialize the state machine
        self.machine = Machine(model=self, states=StartJourneyMachine.states, initial="start", transitions=transitions)
