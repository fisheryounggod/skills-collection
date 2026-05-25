---
name: send-to-kindle
description: "Send Obsidian notes, Markdown/TXT/HTML/DOCX/PDF/EPUB files, or article text to Fisher's Kindle. Use when the user says 发到 Kindle, 发送到 Kindle, Kindle 阅读, Obsidian send-to-kindle, Markdown 转 Kindle, or asks to push reading material to Kindle. Defaults: SMTP smtp.qq.com:465, sender 1632164730@qq.com, Kindle receiver 19182199431@kindle.com."
---

# Send to Kindle

Use this skill to convert local notes/articles to Kindle-friendly files and optionally email them to Fisher's Kindle.

## Defaults

- SMTP host: `smtp.qq.com`
- SMTP SSL port: `465`
- Sender: `1632164730@qq.com`
- Kindle receiver: `19182199431@kindle.com`
- Obsidian vault: `${OBSIDIAN_VAULT_PATH}` or `/Users/mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/oneinall`
- Output dir: `/Users/mac/hermes/kindle`
- Default format: `epub`

## Prerequisite

The non-secret defaults are stored in `/Users/mac/.hermes/config/send-to-kindle.env`. The script auto-loads this file.

QQ Mail SMTP requires an authorization code, not the QQ login password. Before sending email, add one of these to `/Users/mac/.hermes/config/send-to-kindle.env` or the shell environment:

```bash
QQ_SMTP_AUTH_CODE=your_qq_mail_authorization_code
# or
KINDLE_SMTP_PASSWORD=your_qq_mail_authorization_code
```

If no password is configured, still generate the EPUB/PDF and tell Fisher the local path.

## Commands

Convert an Obsidian note title or local file to EPUB without sending:

```bash
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "note title or /path/file.md"
```

Convert and send:

```bash
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "note title or /path/file.md" --send
```

Force output format:

```bash
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "note.md" --format pdf
```

Cover/title/author options:

```bash
# Auto cover is enabled by default
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "raw/article.md"

# Use a specific cover image
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --cover "sources/attachments/cover.jpg"

# Disable cover or TOC
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --cover none --no-toc

# Override metadata
python /Users/mac/.hermes/skills/productivity/send-to-kindle/scripts/send_to_kindle.py "raw/article.md" --title "Book Title" --author "Fisher"
```

## Plugin-like features

- Reads frontmatter metadata: `title`, `bookTitle`, `author`, `authors`, `date`, `description`, `summary`, `url`, `source`, `cover`, `image`, `thumbnail`.
- Generates a Kindle-style e-ink cover automatically when no cover image is found.
- Uses frontmatter cover/image or the first embedded Obsidian image as EPUB cover when available.
- Converts Obsidian embeds and wikilinks: `![[image.png]]`, `[[Note|Alias]]`, `[[Note]]`.
- Adds EPUB metadata, Chinese language tag, CSS, and table of contents by default.

## Workflow

1. Resolve the input:
   - Existing absolute/relative file path: use it directly.
   - Obsidian-relative paths like `obsidian/raw/title.md`, `oneinall/raw/title.md`, or `raw/title.md`: resolve against the configured vault.
   - Otherwise search the Obsidian vault for an exact filename match, then fuzzy filename match, then content match.
2. Normalize Obsidian Markdown:
   - Parse frontmatter.
   - Convert wikilinks and embedded images.
   - Resolve images from note folder, vault root, and `sources/attachments`.
3. Convert Markdown/TXT/HTML/DOCX to EPUB with pandoc, including cover, CSS, TOC, metadata.
4. Keep PDF/EPUB as-is unless conversion or metadata/cover changes are explicitly requested.
5. If `--send` is requested, send via QQ SMTP SSL to the Kindle address.
6. Verify the output file exists and report the path, size, title, author, cover, CSS, and send status.

## Pitfalls

- If email reports success but Kindle does not receive it, check Amazon `Approved Personal Document E-mail List` contains `1632164730@qq.com`.
- Use QQ Mail authorization code, not QQ password.
- Large files may be rejected by Kindle email; keep attachments under roughly 50 MB.
- For academic PDFs, prefer sending the original PDF instead of converting to EPUB.
