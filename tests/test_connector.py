from connectors.sample_dataset.connector import SampleDatasetConnector


def test_sample_connector_returns_valid_records():
    records = SampleDatasetConnector().collect()

    assert len(records) >= 5
    assert all(record.source for record in records)
    assert all(record.source_url for record in records)

