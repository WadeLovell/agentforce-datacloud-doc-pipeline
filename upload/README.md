# Data Cloud Ingestion

This directory handles ingestion of procedure-level Markdown files
into Salesforce Data Cloud Unstructured Data for Agentforce retrieval.

## POC Usage

1. Copy `env.example` → `.env`
2. Populate Salesforce + Data Cloud values:
   - Create a Connected App in Salesforce Setup
   - Enable OAuth for "Full access" (POC only)
   - Copy Client ID and Secret
3. Run pipeline:
   ```bash
   make all
   python upload/datacloud_ingest.py
   ```

## Result

- Documents are indexed in Data Cloud
- Metadata is available for semantic filtering
- Ready for Agentforce Prompt Builder binding

## Production Hardening (Future)

When moving from POC to production:

1. **JWT OAuth** - Replace username/password with certificate-based auth
2. **Batch Ingestion** - Use Data Cloud bulk APIs for large datasets
3. **Idempotent Upserts** - Add checksum field to enable updates without duplicates
4. **Version Diffing** - Only re-ingest changed procedures
5. **Scheduled Re-indexing** - Automate nightly rebuilds

## Middle-Market Banking Considerations

- Ensure Connected App has appropriate IP restrictions
- Use sandbox for initial testing
- Document audit trail for compliance review
- Consider FSC Data Kit integration for unified data model
