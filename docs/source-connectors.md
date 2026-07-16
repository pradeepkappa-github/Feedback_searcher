# Source Connectors

The source connector layer is designed for compliant public-feedback collection. It does not scrape social platforms.

## Supported Connector Shells

- LinkedIn
- Facebook
- Instagram
- X
- Truth Social
- Reddit
- Telecom community forums

## Modes

`mock` mode creates realistic telecom feedback records for local development and tests.

`public_feed` mode is currently implemented for Reddit through public RSS search feeds. It is useful for proving live ingestion, but may be rate-limited and should be replaced with official API access for production.

`official_api` mode is reserved for provider-specific SDK/API implementation. Each connector validates that required credentials exist, then raises a clear not-implemented message until the provider client is added.

## Credential Environment Variables

- `LINKEDIN_ACCESS_TOKEN`
- `FACEBOOK_ACCESS_TOKEN`
- `INSTAGRAM_ACCESS_TOKEN`
- `X_BEARER_TOKEN`
- `TRUTHSOCIAL_ACCESS_TOKEN`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

## Compliance Rules

- Use official APIs, approved exports, written permission, or legally permitted public datasets.
- Respect platform terms, robots rules where applicable, privacy requirements, and rate limits.
- Store source URLs and anonymized author references.
- Store public author display names/profile URLs only when the source feed/API explicitly exposes them.
- Do not infer real-world identity, contact details, employer, location, or private attributes from a username.
- Do not collect private, gated, or personal data without explicit authorization.
- Keep connector-specific policy checks close to each connector implementation.
