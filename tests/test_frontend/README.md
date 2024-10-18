# End-to-End tests
We use playwright for end-to-end testing.
To run the end-to-end tests for licensing:\
`invoke frontendtests`

## Test structure
Tests are currently organised in folders corresponding to the views. Within each folder, each view/step of apply-for-a-licence will have its own testfile.

### Good to know
- After running the tests, you may need to run the next test command with the `--create-db` flag to reset the test database.
- After running frontend tests, you can view the test results in the `video-test-results` folder.
- If you want to see the tests in action, you can set the `HEADLESS` environment variable to `False` before running the tests.

## Useful Commands
- A useful command for writing end-to-end tests is:\
`pipenv run playwright codegen http://apply-for-a-licence:8000/`

- If you run into issues running playwright, you may need to install the playwright dependencies:\
`playwright install`
