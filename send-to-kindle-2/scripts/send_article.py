#!/usr/bin/env python3
"""Convert article text to Kindle-ready EPUB and email it.

Usage:
  python3 send_article.py <title> <author> <body_file> [--send]
  python3 send_article.py "Title" "Author" /tmp/body.txt --send

The EPUB is saved to ~/hermes/kindle/<title>.epub
With --send, also attaches to himalaya envelope (himalaya must be configured).
"""

import os
import sys
import zipfile
import uuid
import argparse

KINDLE_EMAIL = "19182199431@kindle.com"
OUTPUT_DIR = os.path.expanduser("~/hermes/kindle")


def make_epub(title: str, author: str, body_text: str, output_path: str = None) -> str:
    """Generate a minimal valid EPUB."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Sanitize filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
    if not output_path:
        output_path = os.path.join(OUTPUT_DIR, f"{safe_title}.epub")

    # Build XHTML with proper Chinese typography
    html_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{title}</title>
  <style>
    body {{
      font-family: "PingFang SC", "Microsoft YaHei", "Hei", sans-serif;
      margin: 5%;
      line-height: 1.8;
      font-size: 1em;
    }}
    h1 {{
      text-align: center;
      color: #333;
      border-bottom: 2px solid #1a9f4f;
      padding-bottom: 10px;
    }}
    p {{
      text-indent: 2em;
      margin: 0.6em 0;
    }}
    h2 {{
      color: #1a9f4f;
      margin-top: 1.5em;
      border-left: 4px solid #1a9f4f;
      padding-left: 10px;
    }}
    h3 {{
      color: #555;
      margin-top: 1.2em;
    }}
    ul, ol {{
      margin: 0.5em 0;
      padding-left: 2em;
    }}
    li {{
      margin: 0.3em 0;
    }}
    blockquote {{
      background: #f5f5f5;
      border-left: 3px solid #1a9f4f;
      padding: 10px;
      margin: 1em 0;
    }}
    .meta {{
      text-align: center;
      color: #888;
      font-size: 0.85em;
      margin-bottom: 2em;
    }}
  </style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">作者：{author}</p>
{body_text}
</body>
</html>'''

    container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPF/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

    book_uuid = str(uuid.uuid4())
    content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:language>zh-CN</dc:language>
    <dc:identifier id="BookId">urn:uuid:{book_uuid}</dc:identifier>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>'''

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
        epub.writestr("META-INF/container.xml", container_xml)
        epub.writestr("OEBPF/content.opf", content_opf)
        epub.writestr("OEBPF/chapter1.xhtml", html_body)

    return output_path


def send_via_himalaya(epub_path: str, sender_email: str):
    """Send EPUB to Kindle via himalaya CLI."""
    # Check himalaya is configured
    import subprocess
    result = subprocess.run(["himalaya", "account", "list"], capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠️ himalaya not configured. Run: himalaya wizard")
        return False

    # Build the email
    cmd = [
        "himalaya", "envelope", "new",
        "--from", sender_email,
        "--to", KINDLE_EMAIL,
        "--subject", f"Kindle: {os.path.basename(epub_path)}",
        "--body", "Send to Kindle",
        "--attachment", epub_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Failed to create envelope: {result.stderr}")
        return False

    # Send
    result = subprocess.run(["himalaya", "envelope", "send"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Sent {epub_path} to {KINDLE_EMAIL}")
        return True
    else:
        print(f"⚠️ Failed to send: {result.stderr}")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="Send article to Kindle as EPUB")
    parser.add_argument("title", help="Article title")
    parser.add_argument("author", help="Article author")
    parser.add_argument("body_file", help="Path to body text file (UTF-8)")
    parser.add_argument("--send", action="store_true", help="Send via himalaya after creating EPUB")
    parser.add_argument("--sender", default=None, help="Sender email (required with --send)")
    parser.add_argument("--output", default=None, help="Output EPUB path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Read body
    with open(args.body_file, "r", encoding="utf-8") as f:
        body_text = f.read()

    # Convert paragraphs to <p> tags
    paragraphs = body_text.strip().split("\n")
    html_paragraphs = []
    in_list = False
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Detect list items
        if para.startswith(("•", "- ", "·", "∗")) or para.match(r"^\d+[.)].*"):
            para = f"<li>{para.lstrip('•-·∗ ')}</li>"
        else:
            para = f"<p>{para}</p>"
        html_paragraphs.append(para)

    body_html = "\n".join(html_paragraphs)

    # Generate EPUB
    epub_path = make_epub(args.title, args.author, body_html, args.output)
    print(f"📖 EPUB created: {epub_path}")
    print(f"   Size: {os.path.getsize(epub_path):,} bytes")

    # Send if requested
    if args.send:
        if not args.sender:
            print("⚠️ --sender required when using --send")
            sys.exit(1)
        send_via_himalaya(epub_path, args.sender)