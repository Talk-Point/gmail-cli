"""Email address parsing utilities."""

from email.utils import parseaddr


def parse_email_address(address: str) -> tuple[str, str]:
    """Parse an email address string into name and email.

    Uses the standard library's email.utils.parseaddr for safe parsing.

    Args:
        address: Email address string, e.g. "John Doe <john@example.com>"
                 or just "john@example.com"

    Returns:
        Tuple of (name, email). Name may be empty string if not present.

    Examples:
        >>> parse_email_address("John Doe <john@example.com>")
        ('John Doe', 'john@example.com')
        >>> parse_email_address("john@example.com")
        ('', 'john@example.com')
        >>> parse_email_address("'Max' via Support <support@example.com>")
        ("'Max' via Support", 'support@example.com')
    """
    name, email = parseaddr(address)
    return name, email


def extract_email(address: str) -> str:
    """Extract just the email address from an address string.

    Args:
        address: Email address string, e.g. "John Doe <john@example.com>"

    Returns:
        The email address part only.

    Examples:
        >>> extract_email("John Doe <john@example.com>")
        'john@example.com'
        >>> extract_email("john@example.com")
        'john@example.com'
    """
    _, email = parseaddr(address)
    return email if email else address


def extract_name(address: str) -> str:
    """Extract just the display name from an address string.

    Args:
        address: Email address string, e.g. "John Doe <john@example.com>"

    Returns:
        The display name, or the full address if no name present.

    Examples:
        >>> extract_name("John Doe <john@example.com>")
        'John Doe'
        >>> extract_name("john@example.com")
        'john@example.com'
    """
    name, email = parseaddr(address)
    return name if name else email if email else address
