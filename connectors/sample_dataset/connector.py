from datetime import UTC, datetime

from shared.schemas.feedback import RawFeedbackRecord


class SampleDatasetConnector:
    name = "Seeded Telecom Public Feedback"

    def collect(self) -> list[RawFeedbackRecord]:
        return [
            RawFeedbackRecord(
                source="Reddit",
                source_url="https://example.com/reddit/att-fiber-dallas",
                company_hint="AT&T",
                product_hint="Fiber",
                text=(
                    "AT&T fiber has been down in North Dallas since noon and the appointment "
                    "moved twice."
                ),
                published_at=datetime(2026, 7, 15, 14, 30, tzinfo=UTC),
                author_reference="anon-7a91",
                location="Dallas, TX",
            ),
            RawFeedbackRecord(
                source="Complaint Dataset",
                source_url="https://example.com/complaints/att-billing-activation",
                company_hint="AT&T",
                product_hint="Wireless",
                text=(
                    "My first AT&T wireless bill had two activation fees and a roaming charge "
                    "I never agreed to."
                ),
                published_at=datetime(2026, 7, 15, 10, 12, tzinfo=UTC),
                author_reference="anon-4f22",
                location="Houston, TX",
            ),
            RawFeedbackRecord(
                source="App Store",
                source_url="https://example.com/appstore/verizon-support",
                company_hint="Verizon",
                product_hint="Wireless",
                text=(
                    "The Verizon app finally let me change my plan without calling support. "
                    "Coverage is reliable."
                ),
                published_at=datetime(2026, 7, 14, 18, 1, tzinfo=UTC),
                author_reference="anon-19b0",
                location="Chicago, IL",
            ),
            RawFeedbackRecord(
                source="Community Forum",
                source_url="https://example.com/forum/tmobile-portin",
                company_hint="T-Mobile",
                product_hint="Postpaid",
                text=(
                    "Switching from Verizon to T-Mobile was easy, but the trade-in promo "
                    "language was confusing."
                ),
                published_at=datetime(2026, 7, 13, 20, 42, tzinfo=UTC),
                author_reference="anon-b501",
                location="Phoenix, AZ",
            ),
            RawFeedbackRecord(
                source="Approved Social API",
                source_url="https://example.com/social/xfinity-cancel",
                company_hint="Xfinity Mobile",
                product_hint="Wireless",
                text=(
                    "Trying to cancel Xfinity Mobile took three chats and each agent gave "
                    "a different answer."
                ),
                published_at=datetime(2026, 7, 12, 9, 35, tzinfo=UTC),
                author_reference="anon-880c",
                location="Philadelphia, PA",
            ),
        ]
