"""Unit tests for Markdown to HTML conversion utilities."""

from gmail_cli.utils.markdown import markdown_to_html, wrap_html_for_email


class TestMarkdownToHtml:
    """Tests for markdown_to_html function."""

    def test_empty_input(self):
        """Empty input returns empty string."""
        result = markdown_to_html("")
        assert result == ""

    def test_plain_text(self):
        """Plain text without Markdown is wrapped in paragraph."""
        result = markdown_to_html("Hello World")
        assert "<p>" in result
        assert "Hello World" in result

    def test_bold_text(self):
        """Bold text is converted to <strong> tags."""
        result = markdown_to_html("**Bold text**")
        assert "<strong>" in result
        assert "Bold text" in result
        assert "</strong>" in result

    def test_italic_text(self):
        """Italic text is converted to <em> tags."""
        result = markdown_to_html("*Italic text*")
        assert "<em>" in result
        assert "Italic text" in result
        assert "</em>" in result

    def test_strikethrough_text(self):
        """Strikethrough text is converted to <del> tags."""
        result = markdown_to_html("~~Strikethrough~~")
        assert "<del>" in result
        assert "Strikethrough" in result
        assert "</del>" in result

    def test_headers_h1_to_h6(self):
        """Headers h1-h6 are converted correctly."""
        for level in range(1, 7):
            result = markdown_to_html(f"{'#' * level} Heading {level}")
            assert f"<h{level}>" in result
            assert f"Heading {level}" in result
            assert f"</h{level}>" in result

    def test_table_basic(self):
        """Basic table is converted to HTML table."""
        markdown = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |"""
        result = markdown_to_html(markdown)
        assert "<table" in result
        assert "<th>" in result or "<th " in result
        assert "Header 1" in result
        assert "<td>" in result or "<td " in result
        assert "Cell 1" in result
        assert "</table>" in result

    def test_table_has_inline_styles(self):
        """Table has inline CSS for email client compatibility."""
        markdown = """| A | B |
|---|---|
| 1 | 2 |"""
        result = markdown_to_html(markdown)
        # Should have inline styles for borders
        assert "style=" in result
        assert "border" in result.lower()

    def test_fenced_code_block(self):
        """Fenced code blocks are converted correctly."""
        markdown = """```python
def hello():
    print("Hello")
```"""
        result = markdown_to_html(markdown)
        assert "<pre>" in result or "<pre " in result
        assert "<code>" in result or "<code " in result
        assert "def hello():" in result

    def test_code_block_has_inline_styles(self):
        """Code blocks have inline CSS styling."""
        markdown = """```
code here
```"""
        result = markdown_to_html(markdown)
        assert "style=" in result
        # Should have monospace font or background styling
        assert "font-family" in result.lower() or "background" in result.lower()

    def test_inline_code(self):
        """Inline code is converted to <code> tags."""
        result = markdown_to_html("Use `print()` function")
        assert "<code" in result  # May have style attribute
        assert "print()" in result
        assert "</code>" in result

    def test_task_list_checked(self):
        """Checked task list items are converted correctly."""
        result = markdown_to_html("- [x] Completed task")
        assert "checkbox" in result.lower() or "checked" in result.lower()
        assert "Completed task" in result

    def test_task_list_unchecked(self):
        """Unchecked task list items are converted correctly."""
        result = markdown_to_html("- [ ] Pending task")
        assert "checkbox" in result.lower() or "type=" in result.lower()
        assert "Pending task" in result

    def test_blockquote(self):
        """Blockquotes are converted to <blockquote> tags."""
        result = markdown_to_html("> This is a quote")
        assert "<blockquote" in result  # May have style attribute
        assert "This is a quote" in result
        assert "</blockquote>" in result

    def test_unordered_list(self):
        """Unordered lists are converted correctly."""
        markdown = """- Item 1
- Item 2
- Item 3"""
        result = markdown_to_html(markdown)
        assert "<ul>" in result
        assert "<li>" in result
        assert "Item 1" in result
        assert "</ul>" in result

    def test_ordered_list(self):
        """Ordered lists are converted correctly."""
        markdown = """1. First
2. Second
3. Third"""
        result = markdown_to_html(markdown)
        assert "<ol>" in result
        assert "<li>" in result
        assert "First" in result
        assert "</ol>" in result

    def test_link(self):
        """Links are converted to <a> tags."""
        result = markdown_to_html("[Example](https://example.com)")
        assert "<a " in result
        assert 'href="https://example.com"' in result
        assert "Example" in result
        assert "</a>" in result

    def test_image(self):
        """Images are converted to <img> tags."""
        result = markdown_to_html("![Alt text](https://example.com/image.png)")
        assert "<img " in result
        assert 'src="https://example.com/image.png"' in result
        assert 'alt="Alt text"' in result

    def test_horizontal_rule(self):
        """Horizontal rules are converted to <hr> tags."""
        result = markdown_to_html("---")
        assert "<hr" in result

    def test_unicode_content(self):
        """Unicode content is preserved correctly."""
        result = markdown_to_html("**日本語** und Ümläüte äöü")
        assert "日本語" in result
        assert "Ümläüte" in result
        assert "äöü" in result


class TestWrapHtmlForEmail:
    """Tests for wrap_html_for_email function."""

    def test_empty_input(self):
        """Empty input returns empty wrapper."""
        result = wrap_html_for_email("")
        # Should still have the wrapper div
        assert "<div" in result or result == ""

    def test_wraps_content_in_div(self):
        """Content is wrapped in a div with font-family."""
        result = wrap_html_for_email("<p>Hello</p>")
        assert "<div" in result
        assert "style=" in result
        assert "font-family" in result.lower()
        assert "<p>Hello</p>" in result

    def test_preserves_existing_html(self):
        """Existing HTML structure is preserved."""
        html = "<strong>Bold</strong><em>Italic</em>"
        result = wrap_html_for_email(html)
        assert "<strong>Bold</strong>" in result
        assert "<em>Italic</em>" in result

    def test_no_html_head_body_tags(self):
        """Does NOT add <html>, <head>, <body> tags (email clients strip them)."""
        result = wrap_html_for_email("<p>Content</p>")
        assert "<html" not in result.lower()
        assert "<head" not in result.lower()
        assert "<body" not in result.lower()
