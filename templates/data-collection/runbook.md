# LAB-XXX: [Dataset / Pipeline Name] — Collection Runbook

## 1. Prerequisites & Source Credentials
- Source API tokens, credentials, or scraping rate limits
- Storage destinations

## 2. Ingestion Commands
```bash
# Run ingestion / scraping pipeline
python run_pipeline.py --source all --output data/
```

## 3. Data Validation & Quality Checks
```bash
# Validate data integrity and schema
python validate_data.py
```

## 4. Troubleshooting & Handling Failures
- Rate limit handling and backoff
- Schema drift recovery
