# End-to-End tests
We use playwright for end-to-end testing.
To run the end-to-end tests for licensing, start the django server using the test config settings:\
`pipenv run python django_app/manage.py runserver --settings=config.settings.test`

To run end-to-end tests only:\
`pipenv run pytest tests/test_frontend`\

Currently, end-to-end test must be run as testfiles separately
e.g. `pipenv run pytest tests/test_frontend/test_business/test_business_details` as there are some issues when they are run as a full test-suite.

## Test structure
Tests are currently organised in folders corresponding to the views. Within each folder, each view/step of apply-for-a-licence will have its own testfile.

## Useful Commands
A useful command for writing end-to-end tests is:\
`pipenv run playwright codegen http://apply-for-a-licence:8000/`

If you run into issues running playwright, you may need to install the playwright dependencies:\
`playwright install`
