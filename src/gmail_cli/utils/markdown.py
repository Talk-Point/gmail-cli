"""Markdown to HTML conversion utility for email body."""

import re

import markdown

# Style constants for email-safe HTML
_EMAIL_WRAPPER_STYLE = (
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', "
    "Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #1f2328;"
)
_INLINE_CODE_STYLE = (
    "background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; "
    "font-family: ui-monospace, SFMono-Regular, monospace; font-size: 85%;"
)


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown text to HTML with email-safe styling.

    Supports GitHub-Flavored Markdown including:
    - Headers (# through ######)
    - Bold (**text**) and italic (*text*)
    - Strikethrough (~~text~~)
    - Tables with alignment
    - Fenced code blocks with language hints
    - Inline code (`code`)
    - Task lists (- [x] and - [ ])
    - Blockquotes (>)
    - Ordered and unordered lists
    - Links and images
    - Horizontal rules (---)

    Args:
        markdown_text: The Markdown-formatted input string.

    Returns:
        HTML string with inline styles for email client compatibility.
        Returns empty string if input is empty.
    """
    if not markdown_text:
        return ""

    # Configure Markdown with GFM extensions
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.nl2br",
            "pymdownx.tilde",  # Strikethrough ~~text~~
            "pymdownx.tasklist",  # Task lists - [x]
        ],
        extension_configs={
            "pymdownx.tasklist": {
                "clickable_checkbox": False,
            },
        },
    )

    # Convert Markdown to HTML
    html = md.convert(markdown_text)

    # Post-process: Add inline CSS for email client compatibility
    html = _add_table_styles(html)
    html = _add_code_styles(html)
    html = _add_blockquote_styles(html)

    return html


def _add_table_styles(html: str) -> str:
    """Add inline CSS to tables for email client compatibility."""
    # Style the table element
    html = re.sub(
        r"<table>",
        '<table style="border-collapse: collapse; width: 100%; margin: 16px 0;">',
        html,
    )

    # Style table headers
    html = re.sub(
        r"<th>",
        '<th style="border: 1px solid #ddd; padding: 8px 12px; background-color: #f6f8fa; text-align: left; font-weight: 600;">',
        html,
    )

    # Style table cells
    html = re.sub(
        r"<td>",
        '<td style="border: 1px solid #ddd; padding: 8px 12px;">',
        html,
    )

    # Style table rows for alternating colors
    html = re.sub(
        r"<tr>",
        '<tr style="border-bottom: 1px solid #ddd;">',
        html,
    )

    return html


def _add_code_styles(html: str) -> str:
    """Add inline CSS to code blocks for email client compatibility."""
    # Style fenced code blocks (pre > code)
    html = re.sub(
        r"<pre>",
        "<pre style=\"background-color: #f6f8fa; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace; font-size: 85%; line-height: 1.45;\">",
        html,
    )

    # Style code elements inside pre (remove extra styling since pre handles it)
    html = re.sub(
        r"<pre([^>]*)><code([^>]*)>",
        r"<pre\1><code\2 style=\"font-family: inherit; font-size: inherit; background: none; padding: 0;\">",
        html,
    )

    # Style inline code (not inside pre)
    # We already styled code inside pre above, so now style remaining <code> tags
    # that don't have a style attribute yet (these are inline code)
    html = re.sub(
        r"<code(?![^>]*style=)([^>]*)>",
        rf'<code style="{_INLINE_CODE_STYLE}"\1>',
        html,
    )

    return html


def _add_blockquote_styles(html: str) -> str:
    """Add inline CSS to blockquotes for email client compatibility."""
    html = re.sub(
        r"<blockquote>",
        '<blockquote style="margin: 16px 0; padding: 0 16px; color: #656d76; border-left: 4px solid #d0d7de;">',
        html,
    )

    return html


def wrap_html_for_email(html_body: str) -> str:
    """Wrap HTML content in a basic email-safe HTML document structure.

    Args:
        html_body: The HTML body content (e.g., from markdown_to_html).

    Returns:
        Complete HTML with basic styling wrapper.

    Note:
        Does NOT add <html>, <head>, <body> tags as email clients strip them.
        Wraps in <div> with font-family for consistent rendering.
    """
    if not html_body:
        return f'<div style="{_EMAIL_WRAPPER_STYLE}"></div>'

    return f'<div style="{_EMAIL_WRAPPER_STYLE}">{html_body}</div>'
