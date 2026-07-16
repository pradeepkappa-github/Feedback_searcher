import os

from connectors.social.platforms import build_connector
from shared.schemas.sources import SourceConnectorConfig


def connector_configs(mode: str = "mock") -> list[SourceConnectorConfig]:
    return [
        SourceConnectorConfig(
            name="LinkedIn",
            platform="linkedin",
            mode=mode,
            access_token_env="LINKEDIN_ACCESS_TOKEN",
            policy_note=(
                "Use approved LinkedIn APIs and permitted organization/content access only."
            ),
        ),
        SourceConnectorConfig(
            name="Facebook",
            platform="facebook",
            mode=mode,
            access_token_env="FACEBOOK_ACCESS_TOKEN",
            policy_note="Use Meta Graph API with app review and permitted public page data only.",
        ),
        SourceConnectorConfig(
            name="Instagram",
            platform="instagram",
            mode=mode,
            access_token_env="INSTAGRAM_ACCESS_TOKEN",
            policy_note="Use Instagram Graph API for authorized business/creator access.",
        ),
        SourceConnectorConfig(
            name="X",
            platform="x",
            mode=mode,
            access_token_env="X_BEARER_TOKEN",
            policy_note=(
                "Use the official X API plan that permits search/retrieval for this use case."
            ),
        ),
        SourceConnectorConfig(
            name="Truth Social",
            platform="truthsocial",
            mode=mode,
            access_token_env="TRUTHSOCIAL_ACCESS_TOKEN",
            policy_note="Use permitted API access or approved export; scraping is disabled.",
        ),
        SourceConnectorConfig(
            name="Reddit",
            platform="reddit",
            mode=mode,
            client_id_env="REDDIT_CLIENT_ID",
            client_secret_env="REDDIT_CLIENT_SECRET",
            policy_note="Use Reddit API/OAuth with user agent, subreddit rules, and rate limits.",
        ),
        SourceConnectorConfig(
            name="Telecom Community Forums",
            platform="telecom_community",
            mode=mode,
            policy_note=(
                "Use site-approved APIs, feeds, or written permission; robots and ToS "
                "review required."
            ),
        ),
    ]


def build_social_connectors(mode: str = "mock"):
    connectors = []
    for config in connector_configs(mode):
        credential_env = config.access_token_env or config.client_id_env
        credential = os.getenv(credential_env, "") if credential_env else None
        connectors.append(build_connector(config, credential))
    return connectors
