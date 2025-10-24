# Jules Provenance System

This document outlines the architecture and usage of the Jules provenance system.

## Overview

The Jules provenance system is designed to track the origin and transformation of data within the `llm_echo` pipeline. It emits provenance events, which are JSON objects that conform to the schema defined in `.github/PROVENANCE_SCHEMA.json`. These events are stored as individual files in the `.github/PROVENANCE/` directory.

## Usage

### Command-Line Interface

The `scrapeandemit.py` script provides a command-line interface for scraping a URL, processing it with the DeepSeek API, and emitting a provenance event.

To use the script, run the following command:

```bash
python scripts/scrapeandemit.py <URL>
```

You can also perform a dry run, which will print the event to the console without writing it to a file:

```bash
python scripts/scrapeandemit.py <URL> --dry-run
```

### GitHub Actions Workflow

The provenance system can also be triggered automatically using a GitHub Actions workflow. The workflow is defined in `.github/workflows/deepseekscrape.yml` and can be triggered in the following ways:

*   **Manual trigger:** The workflow can be triggered manually from the GitHub Actions tab.
*   **Repository dispatch:** The workflow can be triggered by a `repository_dispatch` event with the `deepseek-scrape` event type.
*   **Issue comment:** The workflow can be triggered by creating a comment on a pull request that starts with `/deepseek-scan <URL>`.

## Schema

The provenance event schema is defined in `.github/PROVENANCE_SCHEMA.json`. All events emitted by the system must conform to this schema.

## Testing

To run the tests for the provenance system, run the following command:

```bash
python -m unittest discover tests
```
