---
name: send-to-kindle
description: "Fetch any URL/article, convert to EPUB, email to Fisher's Kindle (19182199431@kindle.com). One command: '发到kindle <URL>'."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
prerequisites:
  commands: [himalaya, python3, brew]
  env:
    KINDLE_EMAIL: "19182199431@kindle.com"
metadata:
  hermes:
    tags: [kindle, epub, email, content-conversion]
---

# Send-to-Kindle

One command to fetch any URL and deliver it as an EPUB to Fisher's Kindle.

## Usage

```
发到kindle <URL>
发到kindle https://x.com/user/status/123456
发到kindle https://mp.weixin.qq.com/s/xxxxx
```

## Workflow

### Step 1: Fetch Content

**X/Twitter posts** → use browser + `browser_console` to extract `article.innerText`:
```js
(() => { const a = document.querySelector('article'); return a ? a.innerText : ''; })()
```

**WeChat articles** → use `baoyu-url-to-markdown` skill or `baoyu-fetch` CLI:
```bash
cd ~/.hermes/skills/baoyu-url-to-markdown/scripts/ && ~/.bun/bin/bun lib/cli.ts <url> --output /tmp/kindle_raw.md
```

**Other URLs** → use `baoyu-url-to-markdown` or `browser_navigate` + `browser_console`.

### Step 2: Convert to EPUB

Python script generates a minimal valid EPUB:

```python
#!/usr/bin/env python3
"""Convert text to Kindle-ready EPUB."""
import os, zipfile

title = "Article Title"
author = "Author Name"
body = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><title>' + title + '</title><style>body{font-family:"PingFang SC","Microsoft YaHei",sans-serif;margin:5%;line-height:1.8;}h1{text-align:center;color:#333;border-bottom:2px solid #1a9f4f;padding-bottom:10px;}p{text-indent:2em;margin:0.5em 0;}</style></head><body><h1>' + title + '</h1><p>' + body_text.replace('\n', '</p><p>') + '</p></body></html>'

output_dir = os.path.expanduser("~/hermes/kindle")
os.makedirs(output_dir, exist_ok=True)
epub_path = os.path.join(output_dir, "kindle.epub")

with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub:
    epub.writestr("META-INF/container.xml", '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPF/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
    epub.writestr("OEBPF/content.opf", '<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>' + title + '</dc:title><dc:creator>' + author + '</dc:creator><dc:language>zh-CN</dc:language><dc:identifier id="BookId">urn:uuid:' + 'a'*36 + '</dc:identifier></metadata><manifest><item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="chapter1"/></spine></package>')
    epub.writestr("OEBPF/chapter1.xhtml", body)

print(f"EPUB: {epub_path}")
```

### Step 3: Send via Email

Use `himalaya` (already installed via `brew install himalaya`).

**Prerequisite**: himalaya must be configured with SMTP credentials (Gmail app password recommended).

Send with himalaya:
```bash
himalaya envelope new \
  --from "YOUR_EMAIL@gmail.com" \
  --to "19182199431@kindle.com" \
  --subject "Send to Kindle" \
  --body "Attached" \
  --attachment ~/hermes/kindle/kindle.epub
himalaya envelope send
```

If himalaya is not configured, **ask Fisher for**:
1. Sender email address
2. Gmail app password (16-char, NOT login password)

> ⚠️ Gmail requires app password, not login password. Create at: Google Account → Security → 2-Step Verification → App Passwords.

## Verification

After sending, confirm the EPUB:
- Path: `~/hermes/kindle/kindle.epub`
- Size: should be 5-50KB depending on content length

## Pitfalls

- **xurl not installed**: use browser instead for X posts
- **baoyu-url-to-markdown shell wrapper fails**: run bun directly: `cd scripts/ && ~/.bun/bin/bun lib/cli.ts <url>`
- **himalaya not configured**: ask Fisher for SMTP credentials before attempting send
- **Chinese font missing on Kindle**: use `PingFang SC` fallback in CSS font-family

---
Last Updated: 2026-05-25