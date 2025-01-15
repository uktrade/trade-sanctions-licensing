# Default name used when saving a user record for a new GOV.UK One Login user.
# We need this because GOV.UK One Login will not provide name data without identity verification.
ONE_LOGIN_UNSET_NAME = "one_login_unset"
AUTHENTICATION_LEVEL = "Cl.Cm"  # username, password, and 2fa
CONFIDENCE_LEVEL = "P0"  # no identity verification
LOGIN_SCOPE = "openid email"  # required scopes for login
