class CompaniesHouseException(Exception):
    """Exception raised when issue encountered with Companies House API"""

    pass


class CompaniesHouse500Error(Exception):
    """Exception raised when the Companies House API returns a 500 error"""

    pass


class EmailNotVerifiedException(Exception):
    """Exception raised when user tries to save a licence without verifying their email address."""

    pass
