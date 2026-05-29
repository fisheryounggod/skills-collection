---
name: send-to-kindle
description: "Convert notes/articles/Markdown/text/X posts to EPUB and email to Fisher's Kindle (19182199431@kindle.com). Triggers: 发到Kindle, 发送到Kindle, 发到kindle, Markdown转Kindle, X帖子发Kindle. Default: QQ SMTP smtp.qq.com:465, sender 1632164730@qq.com. Skill file: /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
prerequisites:
  commands: [python3, pandoc, brew]
  env:
    KINDLE_EMAIL: "19182199431@kindle.com"
    SMTP_HOST: "smtp.qq.com"
    SMTP_PORT: "465"
    SENDER_EMAIL: "1632164730@qq.com"
metadata:
  hermes:
    tags: [kindle, epub, email, content-conversion, qq-mail]
---

# Send-to-Kindle

Convert any content (Obsidian note, Markdown, TXT, X/Twitter post, article URL) to EPUB and optionally email it to Fisher's Kindle.

## Script Location

```bash
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py [...]
```

The script auto-loads defaults from `/Users/mac/.hermes/config/send-to-kindle.env`.

## Default Config

| Item | Value |
|------|-------|
| SMTP host | `smtp.qq.com` |
| SMTP SSL port | `465` |
| Sender | `1632164730@qq.com` |
| Kindle receiver | `19182199431@kindle.com` |
| Obsidian vault | `/Users/mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/oneinall` |
| Output dir | `/Users/mac/hermes/kindle` |
| Default author | `***` (hidden) |

## Prerequisites

### 1. pandoc (required for .txt/.md conversion)

```bash
brew install pandoc
```

### 2. QQ Mail Authorization Code

QQ SMTP requires an **authorization code** (NOT the QQ login password). Add to `/Users/mac/.hermes/config/send-to-kindle.env`:

```bash
QQ_SMTP_AUTH_CODE=your_qq_mail_authorization_code
# or
KINDLE_SMTP_PASSWORD=your_qq_mail_authorization_code
```

Get the code: QQ Mail → Settings → Account → POP3/SMTP/IMAP → Enable → Generate Authorization Code.

If no password is configured, the script still generates the EPUB but skips sending.

## Commands

### Basic: convert + send

```bash
# Convert and send (use absolute path for arbitrary files)
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "/path/to/file.txt" --send

# Obsidian vault relative path
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --send

# Convert only (no email)
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "/path/to/file.txt"
```

### Override options

```bash
# Force PDF/EPUB format
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "/path/file.pdf" --format pdf --send

# Custom title / author
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --title "Book Title" --author "Author" --send

# Custom cover image
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --cover "sources/attachments/cover.jpg" --send

# No cover, no TOC
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --cover none --no-toc --send
```

### SMTP overrides (via CLI)

```bash
--smtp-host smtp.gmail.com --smtp-port 587 --sender you@gmail.com --receiver 19182199431@kindle.com
```

## Workflow by Source Type

### X / Twitter Posts

1. `browser_navigate` to tweet URL
2. `browser_console` extract:
   ```js
   (() => { const a = document.querySelector('article'); return a ? a.innerText : ''; })()
   ```
3. Save to `/Users/mac/hermes/kindle/<filename>.txt` (use the **file path as the input**, NOT a URL)
4. Run: `python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "/Users/mac/hermes/kindle/<filename>.txt" --send`

### WeChat Articles

```bash
cd ~/.hermes/skills/baoyu-url-to-markdown/scripts/ && ~/.bun/bin/bun lib/cli.ts <url> --output /tmp/article.md
```
Then: `python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "/tmp/article.md" --send`

### Obsidian Notes

```bash
python3 /Users/mac/.hermes/skills/send-to-kindle/scripts/send_to_kindle.py "raw/NoteTitle.md" --send
```

Path resolution: absolute → direct; Obsidian-relative (`obsidian/`, `oneinall/`, `raw/`) → resolved against vault; bare names → searched in vault.

### Plain Text / HTML / DOCX / RTF

Saved directly with pandoc conversion.

## Skill Features

- Reads frontmatter: `title`, `bookTitle`, `author`, `authors`, `date`, `description`, `summary`, `url`, `source`, `cover`, `image`, `thumbnail`
- Auto-generates a Kindle-style e-ink cover when no cover image found
- Converts Obsidian embeds and wikilinks: `![[image.png]]`, `[[Note|Alias]]`, `[[Note]]`
- Adds EPUB metadata, Chinese language tag (`zh-CN`), CSS, and TOC by default

## Output

```
source=/path/to/input.txt
output=/Users/mac/hermes/kindle/YYYY-MM-DD/filename.epub
size=52.1 KB
title=...
author=Fisher
cover=/path/to/cover.jpg
css=/path/to/kindle-style.css
```

## Pitfalls

- **Missing SMTP password**: Generates EPUB but skips send. Configure `QQ_SMTP_AUTH_CODE` in `/Users/mac/.hermes/config/send-to-kindle.env`. EPUB still saved locally.
- **pandoc not found**: Run `brew install pandoc` — without it, `.txt`/`.md`/`.html` conversion fails.
- **Kindle not receiving**: Check Amazon "Approved Personal Document E-mail List" contains `1632164730@qq.com`.
- **Large files**: Keep attachments under ~50 MB; Kindle rejects oversized emails.
- **baoyu-url-to-markdown shell wrapper fails**: Run bun directly: `cd scripts/ && ~/.bun/bin/bun lib/cli.ts <url>`.
- **xurl not installed**: Use browser + `browser_console` instead for X posts.
- **Input resolved as non-existent**: Use absolute paths for files outside Obsidian vault. The script does NOT treat arbitrary paths as vault-relative.

---
Last Updated: 2026-05-25
