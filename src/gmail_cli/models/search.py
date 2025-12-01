"""Search result model."""

from dataclasses import dataclass

from gmail_cli.models.email import Email


@dataclass
class SearchResult:
    """Paginated search result."""

    emails: list[Email]
    total_estimate: int
    next_page_token: str | None
    query: str
