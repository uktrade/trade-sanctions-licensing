#
# @pytest.mark.django_db
# @patch("apply_for_a_licence.views.views_end.SaveToDB", return_value=MagicMock())
# @patch("apply_for_a_licence.views.views_end.send_email", new=MagicMock())
# class TestDeclarationView:
#     """We're just testing the view logic here, not the chunky save_to_db stuff"""
#
#     @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
#     def test_is_individual(self, patched_clean_data, patched_save_to_db, al_client):
#         session = InfiniteDict()
#         session["start"]["who_do_you_want_the_licence_to_cover"] = "individual"
#         patched_clean_data.return_value = session
#         patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()
#
#         al_client.post(reverse("declaration"), data={"declaration": "on"})
#         assert patched_save_to_db.called_with(is_individual=True)
#         assert patched_save_to_db.called_with(business_employing_individual=True)
#         assert patched_save_to_db.called_with(is_third_party=False)
#         assert patched_save_to_db.return_value.save_individuals.called
#
#         session["start"]["who_do_you_want_the_licence_to_cover"] = "myself"
#         patched_clean_data.return_value = session
#         patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()
#
#         al_client.post(reverse("declaration"), data={"declaration": "on"})
#         assert patched_save_to_db.called_with(is_individual=True)
#         assert patched_save_to_db.called_with(business_employing_individual=False)
#         assert patched_save_to_db.called_with(is_third_party=False)
#
#     @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
#     def test_is_on_companies_house(self, patched_clean_data, patched_save_to_db, al_client):
#         session = InfiniteDict()
#         session["is_the_business_registered_with_companies_house"]["business_registered_on_companies_house"] = "yes"
#         session["do_you_know_the_registered_company_number"]["do_you_know_the_registered_company_number"] = "yes"
#         patched_clean_data.return_value = session
#         patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()
#
#         al_client.post(reverse("declaration"), data={"declaration": "on"})
#         assert patched_save_to_db.called_with(is_on_companies_house=True)
#         assert patched_save_to_db.called_with(is_third_party=False)
#         assert patched_save_to_db.called_with(is_individual=False)
#
#     @patch("apply_for_a_licence.views.views_end.get_all_cleaned_data")
#     def test_is_third_party(self, patched_clean_data, patched_save_to_db, al_client):
#         session = InfiniteDict()
#         session["are_you_third_party"]["are_you_applying_on_behalf_of_someone_else"] = "True"
#         patched_clean_data.return_value = session
#         patched_save_to_db.return_value.save_licence.return_value = LicenceFactory()
#
#         al_client.post(reverse("declaration"), data={"declaration": "on"})
#         assert patched_save_to_db.called_with(is_third_party=True)
#         assert patched_save_to_db.called_with(is_on_companies_house=False)
#         assert patched_save_to_db.called_with(is_individual=True)
