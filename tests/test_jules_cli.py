import pytest
from scripts import jules_cli
from unittest.mock import patch, MagicMock


@patch("scripts.jules_cli.scrape")
def test_dispatch_scrape(mock_scrape):
    args = MagicMock()
    args.comment = "/deepseek-scan https://example.com"
    args.dry_run = False
    with patch.dict(
        "os.environ", {"GITHUB_ISSUE_NUMBER": "123"}, clear=True
    ):
        jules_cli.dispatch(args)
    mock_scrape.assert_called_once()
    call_args = mock_scrape.call_args[0][0]
    assert call_args.url == "https://example.com"
    assert call_args.claimid == "123"


@patch("scripts.jules_cli.parse_qodo")
def test_dispatch_parse_qodo(mock_parse_qodo):
    args = MagicMock()
    args.comment = "/qodo-feedback"
    args.dry_run = False
    with patch.dict(
        "os.environ",
        {"GITHUB_REPOSITORY": "owner/repo", "GITHUB_ISSUE_NUMBER": "456"},
        clear=True,
    ):
        jules_cli.dispatch(args)
    mock_parse_qodo.assert_called_once()
    call_args = mock_parse_qodo.call_args[0][0]
    assert call_args.repo == "owner/repo"
    assert call_args.pr == 456
