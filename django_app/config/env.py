import os
from typing import Any

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.network import setup_allowed_hosts
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        validate_default=False,
    )

    debug: bool = False
    django_secret_key: str
    licensing_allowed_hosts: list[str] = ["*"]

    clam_av_username: str = ""
    clam_av_password: str = ""
    clam_av_domain: str = ""

    companies_house_api_key: str | None = None

    gov_notify_api_key: str = ""
    email_verify_code_template_id: str = ""
    new_otsi_user_template_id: str = ""
    public_user_new_application_template_id: str = ""
    otsi_new_application_template_id: str = ""
    email_verify_timeout_seconds: int = 3600
    new_application_alert_recipients: str = "email@example.com"

    sentry_dsn: str = ""
    sentry_environment: str = ""
    sentry_enabled: bool = True
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 0.0

    gtm_enabled: bool = True
    gtm_id: str = ""

    temporary_s3_bucket_access_key_id: str = "test"
    temporary_s3_bucket_secret_access_key: str = "test"

    permanent_s3_bucket_access_key_id: str = "test"
    permanent_s3_bucket_secret_access_key: str = "test"

    aws_endpoint_url: str = ""
    aws_default_region: str = "eu-west-2"
    temporary_s3_bucket_name: str = "temporary-document-bucket"
    permanent_s3_bucket_name: str = "permanent-document-bucket"
    presigned_url_expiry_seconds: int = 3600

    # Django sites
    apply_for_a_licence_domain: str = "apply-for-a-licence:8000"
    view_a_licence_domain: str = "view-a-licence:8000"

    apply_for_a_licence_extra_domain: str = ""
    view_a_licence_extra_domain: str = ""

    # SSO
    authbroker_url: str = ""
    authbroker_client_id: str = ""
    authbroker_client_secret: str = ""
    authbroker_token_session_key: str = ""
    authbroker_staff_sso_scope: str = "read"

    mock_sso_token: str = ""
    mock_sso_scope: str = "read"
    mock_sso_username: str = ""
    mock_sso_email_user_id: str = ""
    oauthlib_insecure_transport: int = 0

    # Redis
    redis_host: str = ""
    redis_port: int = 6379

    # Application-specific settings
    otsi_email: str = "email@example.com"

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        return self.licensing_allowed_hosts

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.temporary_s3_bucket_name,
            "access_key_id": self.temporary_s3_bucket_access_key_id,
            "secret_access_key": self.temporary_s3_bucket_secret_access_key,
        }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.permanent_s3_bucket_name,
            "access_key_id": self.permanent_s3_bucket_access_key_id,
            "secret_access_key": self.permanent_s3_bucket_secret_access_key,
        }


class LocalSettings(BaseSettings):
    database_uri: str = Field(alias="DATABASE_URL")
    profiling_enabled: bool = False
    localstack_port: int = 24566


class TestSettings(LocalSettings):
    headless: bool = False
    save_videos: bool = False  # Save videos of the tests


class GovPaasSettings(BaseSettings):
    class VCAPServices(BaseModel):
        model_config = ConfigDict(extra="ignore")

        postgres: list[dict[str, Any]]
        aws_s3_bucket: list[dict[str, Any]] = Field(alias="aws-s3-bucket")
        redis: list[dict[str, Any]]

    vcap_services: VCAPServices | None = VCAPServices

    @computed_field
    @property
    def database_uri(self) -> dict[str, str]:
        return self.vcap_services.postgres[0]["credentials"]["uri"]

    @property
    def get_temporary_bucket_vcap(self) -> dict[str, Any]:
        return next((each["credentials"] for each in self.vcap_services.aws_s3_bucket if "temporary" in each["name"]), {})

    @property
    def get_permanent_bucket_vcap(self) -> dict[str, Any]:
        return next((each["credentials"] for each in self.vcap_services.aws_s3_bucket if "permanent" in each["name"]), {})

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.get_temporary_bucket_vcap["bucket_name"],
            "access_key_id": self.get_temporary_bucket_vcap["aws_access_key_id"],
            "secret_access_key": self.get_temporary_bucket_vcap["aws_secret_access_key"],
        }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict[str, str]:
        return {
            "bucket_name": self.get_permanent_bucket_vcap["bucket_name"],
            "access_key_id": self.get_permanent_bucket_vcap["aws_access_key_id"],
            "secret_access_key": self.get_permanent_bucket_vcap["aws_secret_access_key"],
        }

    @computed_field
    @property
    def redis_url(self) -> str:
        return self.vcap_services.redis[0]["credentials"]["uri"]


class DBTPlatformSettings(BaseSettings):
    in_build_step: bool = Field(alias="BUILD_STEP", default=False)

    # Redis env vars
    redis_endpoint: str = Field(alias="REDIS_ENDPOINT", default="")

    @computed_field
    @property
    def allowed_hosts(self) -> list[str]:
        if self.in_build_step:
            return self.licensing_allowed_hosts
        else:
            return setup_allowed_hosts(self.licensing_allowed_hosts)

    @computed_field
    @property
    def database_uri(self) -> dict[str, str] | str:
        if self.in_build_step:
            return ""
        else:
            return database_url_from_env("DATABASE_CREDENTIALS")

    @computed_field
    @property
    def temporary_s3_bucket_configuration(self) -> dict[str, str]:
        if self.in_build_step:
            return {
                "bucket_name": "",
                "access_key_id": "",
                "secret_access_key": "",
            }
        else:
            return {
                "bucket_name": os.environ.get("TEMPORARY_S3_BUCKET_NAME", ""),
                "access_key_id": None,
                "secret_access_key": None,
            }

    @computed_field
    @property
    def permanent_s3_bucket_configuration(self) -> dict[str, str]:
        if self.in_build_step:
            return {
                "bucket_name": "",
                "access_key_id": "",
                "secret_access_key": "",
            }
        else:
            return {
                "bucket_name": os.environ.get("PERMANENT_S3_BUCKET_NAME", ""),
                "access_key_id": None,
                "secret_access_key": None,
            }

    @computed_field  # type: ignore[misc]
    @property
    def redis_url(self) -> str:
        if self.in_build_step:
            return ""

        return self.redis_endpoint


if "CIRCLECI" in os.environ:
    # CircleCI, don't validate
    # There's a funny issue with capitalisation here, so we casefold() everything in the environ, so we can match it to
    # the properties in the settings models. Everything except for DATABASE_URL which is case-sensitive.
    env = TestSettings.model_construct(
        **{key if key == "DATABASE_URL" else key.casefold(): value for key, value in os.environ.items()}
    )
elif os.environ.get("DJANGO_SETTINGS_MODULE", "") == "config.settings.local":
    # Local development
    env = LocalSettings()
elif os.environ.get("DJANGO_SETTINGS_MODULE", "") == "config.settings.test":
    # Testing
    env = TestSettings()
elif "COPILOT_ENVIRONMENT_NAME" in os.environ:
    # Deployed on DBT Platform
    env = DBTPlatformSettings()
else:
    # Deployed on GOV.PaaS
    env = GovPaasSettings()
