"""Utility functions for Gmail CLI."""

from gmail_cli.utils.html import html_to_text
from gmail_cli.utils.output import (
    console,
    print_error,
    print_json,
    print_success,
    print_table,
)

__all__ = [
    "console",
    "html_to_text",
    "print_error",
    "print_json",
    "print_success",
    "print_table",
]
