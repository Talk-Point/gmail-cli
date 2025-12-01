"""HTML to text conversion utility."""

import html2text


def html_to_text(html_content: str) -> str:
    """Convert HTML content to readable plain text.

    Args:
        html_content: HTML string to convert.

    Returns:
        Plain text representation of the HTML content.
    """
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    return h.handle(html_content).strip()
