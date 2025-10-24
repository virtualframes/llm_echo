# DeepSeek Integration

This document provides details on the integration of the DeepSeek API into the llm_echo pipeline.

## Query Construction

-   **Query Variants**: For each claim, three query variants are generated:
    -   **Concise**: The claim text itself.
    -   **Mechanism-focused**: "How does [claim text] work?"
    -   **Skeptic-focused**: "What is the evidence against the claim that [claim text]?"

## Response Schema

The DeepSeek API is expected to return a list of evidence items, where each item has the following structure:

```json
{
  "evidenceid": "string",
  "url": "string",
  "snippet": "string",
  "title": "string",
  "score": "float",
  "provenanceid": "string"
}
```

## Provenance Fields

The following provenance fields are recorded for each DeepSeek query:

-   `eventtype`: "deepseekquery"
-   `timestampiso`: ISO 8601 timestamp
-   `module`: "search.deepseekadapter"
-   `commitsha`: Git commit SHA
-   `inputhash`: SHA256 hash of the query object
-   `outputhash`: SHA256 hash of the response
-   `provenancetoken`: A unique token for the event
-   `mode`: "real" or "mock"
