from config.env import env_bool
from config.settings import *


# Local defaults remain convenient, but the canonical mdc-catalog/.env can
# override them. Provider publication stays off unless explicitly enabled.
MDC_DEMO_API_ENABLED = env_bool("MDC_DEMO_API_ENABLED", True)
MDC_PROVIDER_PUBLICATION_ENABLED = env_bool(
    "MDC_PROVIDER_PUBLICATION_ENABLED",
    False,
)
