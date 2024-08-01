import factory


class RegimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "apply_for_a_licence.Regime"

    full_name = factory.Faker("name")
