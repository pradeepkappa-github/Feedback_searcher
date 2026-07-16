from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Feedback Finder AI"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    vector_store_path: str = "data/vector_store.json"
    social_connector_mode: str = "mock"
    linkedin_access_token: str = ""
    facebook_access_token: str = ""
    instagram_access_token: str = ""
    x_bearer_token: str = ""
    truthsocial_access_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "FeedbackFinderAI/0.1"
    community_forum_allowed_hosts: str = (
        "community.verizon.com,forums.att.com,community.t-mobile.com,forums.xfinity.com"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def allowed_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def community_forum_hosts(self) -> list[str]:
        return [
            hostname.strip()
            for hostname in self.community_forum_allowed_hosts.split(",")
            if hostname.strip()
        ]


settings = Settings()
