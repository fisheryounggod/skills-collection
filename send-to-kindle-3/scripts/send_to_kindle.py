#!/usr/bin/env python3
"""Convert an Obsidian note/local file to Kindle format and optionally send via QQ SMTP.

Optimized to mimic common Obsidian send-to-kindle plugin behavior:
- vault-relative path resolution
- frontmatter title/author/cover metadata
- Obsidian wikilink and embedded image conversion
- EPUB cover image generation/selection
- EPUB metadata, TOC, CSS
- SMTP email delivery
"""
from __future__ import annotations

import argparse
import email.utils
import mimetypes
import os
import re
import shutil
import smtplib
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

DEFAULT_SMTP_HOST = "smtp.qq.com"
DEFAULT_SMTP_PORT = 465
DEFAULT_FROM = "1632164730@qq.com"
DEFAULT_TO = "19182199431@kindle.com"
DEFAULT_VAULT = "/Users/mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/oneinall"
DEFAULT_OUT = "/Users/mac/hermes/kindle"
DEFAULT_AUTHOR = "Fisher"
CONVERTIBLE = {".md", ".markdown", ".txt", ".html", ".htm", ".docx", ".rtf"}
PASSTHROUGH = {".pdf", ".epub"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
CONFIG_FILE = Path.home() / ".hermes" / "config" / "send-to-kindle.env"


@dataclass
class DocumentMeta:
    title: str
    author: str = DEFAULT_AUTHOR
    date: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    cover: Path | None = None
    source_url: str | None = None
    work_src: Path | None = None
    css: Path | None = None


def load_env_file(path: Path = CONFIG_FILE) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def slugify(value: str, fallback: str = "kindle-document") -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value.strip())
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-. ")
    return value[:120] or fallback


def simple_yaml_value(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return ""
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [simple_yaml_value(x) for x in inner.split(",")]
    return raw


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s+-\s+", line) and current_key:
            meta.setdefault(current_key, [])
            if isinstance(meta[current_key], list):
                meta[current_key].append(simple_yaml_value(re.sub(r"^\s+-\s+", "", line)))
            continue
        if ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            current_key = key.strip()
            meta[current_key] = simple_yaml_value(val)
    return meta, body


def first_value(meta: dict[str, Any], keys: list[str], default: str | None = None) -> str | None:
    for key in keys:
        value = meta.get(key)
        if isinstance(value, list):
            return ", ".join(str(x) for x in value if str(x).strip()) or default
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def resolve_input(query: str, vault: Path) -> Path:
    p = Path(query).expanduser()
    if p.exists():
        return p.resolve()

    normalized_query = query.replace("\\", "/")
    relative_variants = [normalized_query]
    if normalized_query.startswith("obsidian/"):
        relative_variants.append(normalized_query[len("obsidian/") :])
    if normalized_query.startswith("oneinall/"):
        relative_variants.append(normalized_query[len("oneinall/") :])
    for rel in relative_variants:
        candidate = vault / rel
        if candidate.exists():
            return candidate.resolve()

    candidates: list[Path] = []
    if vault.exists():
        q_lower = query.lower()
        exact_name = query if query.lower().endswith(".md") else f"{query}.md"
        for path in vault.rglob("*.md"):
            if path.name == exact_name or path.stem == query:
                return path.resolve()
            if q_lower in path.name.lower() or q_lower in path.stem.lower():
                candidates.append(path)
        if candidates:
            candidates.sort(key=lambda x: (len(str(x)), str(x)))
            return candidates[0].resolve()
        for path in vault.rglob("*.md"):
            try:
                if query in path.read_text(encoding="utf-8", errors="ignore"):
                    return path.resolve()
            except Exception:
                pass
    raise FileNotFoundError(f"Cannot resolve input as file or Obsidian note: {query}")


def resolve_asset(ref: str, src_dir: Path, vault: Path) -> Path | None:
    ref = ref.strip().strip("<>").split("|", 1)[0].strip()
    ref = re.sub(r"^file://", "", ref)
    ref = ref.replace("%20", " ")
    if not ref:
        return None
    p = Path(ref).expanduser()
    if p.exists():
        return p.resolve()
    search_candidates = [src_dir / ref, vault / ref, vault / "sources" / "attachments" / ref, vault / "raw" / ref]
    for c in search_candidates:
        if c.exists():
            return c.resolve()
    # Obsidian links often omit extension. Try common image extensions.
    if Path(ref).suffix == "":
        for ext in IMAGE_EXTS:
            for base in [src_dir, vault / "sources" / "attachments", vault]:
                c = base / f"{ref}{ext}"
                if c.exists():
                    return c.resolve()
    # Last resort by filename, bounded to likely attachment/image locations first.
    name = Path(ref).name
    for root in [vault / "sources" / "attachments", src_dir, vault]:
        if root.exists():
            try:
                for found in root.rglob(name):
                    if found.is_file():
                        return found.resolve()
            except Exception:
                pass
    return None


def convert_obsidian_links(text: str, src_dir: Path, vault: Path) -> tuple[str, list[Path]]:
    embedded_images: list[Path] = []

    def embed_repl(match: re.Match[str]) -> str:
        inner = match.group(1)
        target = inner.split("|", 1)[0].strip()
        resolved = resolve_asset(target, src_dir, vault)
        label = Path(target).stem
        if resolved and resolved.suffix.lower() in IMAGE_EXTS:
            embedded_images.append(resolved)
            return f"![{label}]({resolved.as_posix()})"
        if resolved:
            return f"[{label}]({resolved.as_posix()})"
        return f"[{inner}]"

    def wiki_repl(match: re.Match[str]) -> str:
        inner = match.group(1)
        if "|" in inner:
            target, alias = inner.split("|", 1)
            return alias.strip()
        return inner.strip()

    text = re.sub(r"!\[\[([^\]]+)\]\]", embed_repl, text)
    text = re.sub(r"\[\[([^\]]+)\]\]", wiki_repl, text)

    # Convert ordinary markdown images with vault-relative references where possible.
    def md_img_repl(match: re.Match[str]) -> str:
        alt, ref = match.group(1), match.group(2)
        if ref.startswith(("http://", "https://", "data:")):
            return match.group(0)
        resolved = resolve_asset(ref, src_dir, vault)
        if resolved and resolved.suffix.lower() in IMAGE_EXTS:
            embedded_images.append(resolved)
            return f"![{alt}]({resolved.as_posix()})"
        return match.group(0)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", md_img_repl, text)
    return text, embedded_images


def ensure_css(out_dir: Path) -> Path:
    css = out_dir / "kindle-style.css"
    if not css.exists():
        css.write_text(
            """
body { font-family: serif; line-height: 1.6; }
h1, h2, h3 { line-height: 1.25; margin-top: 1.4em; }
h1 { text-align: center; }
blockquote { border-left: 3px solid #999; margin-left: 0; padding-left: 1em; color: #444; }
code { font-family: monospace; }
pre { white-space: pre-wrap; }
img { max-width: 100%; height: auto; }
hr { border: none; border-top: 1px solid #999; margin: 2em 0; }
""".strip()
            + "\n",
            encoding="utf-8",
        )
    return css


def create_cover(title: str, author: str, out_dir: Path, subtitle: str | None = None) -> Path:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError(f"Pillow is required for auto cover generation: {exc}")

    w, h = 1600, 2560
    img = Image.new("RGB", (w, h), "#f4f0e8")
    draw = ImageDraw.Draw(img)
    # Minimal e-ink style cover.
    draw.rectangle((90, 90, w - 90, h - 90), outline="#111111", width=8)
    draw.rectangle((130, 130, w - 130, h - 130), outline="#777777", width=2)

    def font(size: int, bold: bool = False):
        candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Supplemental/Songti.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                try:
                    return ImageFont.truetype(c, size=size)
                except Exception:
                    pass
        return ImageFont.load_default()

    title_font = font(92, True)
    sub_font = font(42)
    author_font = font(46)

    def wrap(text: str, fnt, max_width: int) -> list[str]:
        chars = list(text)
        lines: list[str] = []
        line = ""
        for ch in chars:
            test = line + ch
            if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = ch
        if line:
            lines.append(line)
        return lines[:9]

    lines = wrap(title, title_font, w - 330)
    total_h = sum(draw.textbbox((0, 0), line, font=title_font)[3] for line in lines) + (len(lines) - 1) * 32
    y = max(520, (h - total_h) // 2 - 180)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (w - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill="#111111", font=title_font)
        y += (bbox[3] - bbox[1]) + 32

    if subtitle:
        sub = subtitle[:80]
        bbox = draw.textbbox((0, 0), sub, font=sub_font)
        draw.text(((w - (bbox[2] - bbox[0])) // 2, y + 50), sub, fill="#555555", font=sub_font)

    author_text = author or DEFAULT_AUTHOR
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    draw.text(((w - (bbox[2] - bbox[0])) // 2, h - 390), author_text, fill="#111111", font=author_font)
    stamp = "Send to Kindle · Hermes"
    bbox = draw.textbbox((0, 0), stamp, font=sub_font)
    draw.text(((w - (bbox[2] - bbox[0])) // 2, h - 280), stamp, fill="#777777", font=sub_font)

    cover = out_dir / f"{slugify(title)}.cover.jpg"
    img.save(cover, quality=92)
    return cover


def normalize_obsidian_markdown(src: Path, out_dir: Path, vault: Path, title_override: str | None, author_override: str | None, cover_arg: str | None) -> DocumentMeta:
    raw = src.read_text(encoding="utf-8", errors="ignore")
    fm, body = split_frontmatter(raw)
    title = title_override or first_value(fm, ["title", "bookTitle", "name"], src.stem) or src.stem
    author = author_override or first_value(fm, ["author", "authors", "creator"], os.getenv("KINDLE_AUTHOR", DEFAULT_AUTHOR)) or DEFAULT_AUTHOR
    date = first_value(fm, ["date", "created", "updated"])
    description = first_value(fm, ["description", "summary", "abstract"])
    source_url = first_value(fm, ["url", "source", "source_url"])
    tags_val = fm.get("tags", [])
    tags = tags_val if isinstance(tags_val, list) else [x.strip() for x in str(tags_val).split(",") if x.strip()]

    body, images = convert_obsidian_links(body, src.parent, vault)
    if source_url and source_url.startswith("http") and source_url not in body[:500]:
        body += f"\n\n---\n\nSource: {source_url}\n"

    cover: Path | None = None
    if cover_arg and cover_arg.lower() not in {"auto", "none"}:
        cover = resolve_asset(cover_arg, src.parent, vault)
        if not cover:
            raise FileNotFoundError(f"Cover not found: {cover_arg}")
    if not cover:
        cover_ref = first_value(fm, ["cover", "image", "coverImage", "thumbnail", "poster"])
        if cover_ref:
            cover = resolve_asset(cover_ref, src.parent, vault)
    if not cover and images:
        cover = images[0]
    if cover_arg == "none":
        cover = None
    if not cover and (cover_arg == "auto" or os.getenv("KINDLE_AUTO_COVER", "1") != "0"):
        cover = create_cover(title, author, out_dir, description)

    normalized = out_dir / f"{slugify(title)}.normalized.md"
    normalized.write_text(body, encoding="utf-8")
    return DocumentMeta(title=title, author=author, date=date, description=description, tags=tags, cover=cover, source_url=source_url, work_src=normalized, css=ensure_css(out_dir))


def metadata_for_non_md(src: Path, out_dir: Path, title_override: str | None, author_override: str | None, cover_arg: str | None, vault: Path) -> DocumentMeta:
    title = title_override or src.stem
    author = author_override or os.getenv("KINDLE_AUTHOR", DEFAULT_AUTHOR)
    cover = None
    if cover_arg and cover_arg.lower() not in {"auto", "none"}:
        cover = resolve_asset(cover_arg, src.parent, vault)
        if not cover:
            raise FileNotFoundError(f"Cover not found: {cover_arg}")
    elif cover_arg != "none" and os.getenv("KINDLE_AUTO_COVER", "1") != "0":
        cover = create_cover(title, author, out_dir)
    return DocumentMeta(title=title, author=author, cover=cover, work_src=src, css=ensure_css(out_dir))


def run_pandoc(src: Path, dst: Path, meta: DocumentMeta, resource_paths: list[Path], toc: bool = True) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc not found. Install pandoc or send PDF/EPUB directly.")
    cmd = [pandoc, str(src), "-o", str(dst)]
    cmd += ["--metadata", f"title={meta.title}"]
    cmd += ["--metadata", f"author={meta.author}"]
    cmd += ["--metadata", "lang=zh-CN"]
    if meta.date:
        cmd += ["--metadata", f"date={meta.date}"]
    if meta.description:
        cmd += ["--metadata", f"description={meta.description}"]
    if dst.suffix.lower() == ".epub":
        if toc:
            cmd += ["--toc", "--toc-depth=3"]
        if meta.cover and meta.cover.exists():
            cmd += ["--epub-cover-image", str(meta.cover)]
        if meta.css and meta.css.exists():
            cmd += ["--css", str(meta.css)]
    paths = []
    for p in resource_paths:
        if p and p.exists():
            paths.append(str(p))
    # Deduplicate while preserving order.
    seen = set()
    paths = [x for x in paths if not (x in seen or seen.add(x))]
    if paths:
        cmd += ["--resource-path", ":".join(paths)]
    subprocess.run(cmd, check=True)


def prepare_file(src: Path, fmt: str, out_dir: Path, vault: Path, title: str | None, author: str | None, cover: str | None, toc: bool) -> tuple[Path, DocumentMeta]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()
    if ext in PASSTHROUGH and fmt == ext.lstrip(".") and not title and not author and not cover:
        dst = out_dir / src.name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
        return dst, DocumentMeta(title=src.stem, author=author or DEFAULT_AUTHOR)
    if ext in PASSTHROUGH and fmt == "original":
        dst = out_dir / src.name
        if src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
        return dst, DocumentMeta(title=src.stem, author=author or DEFAULT_AUTHOR)
    if ext not in CONVERTIBLE and ext not in PASSTHROUGH:
        raise ValueError(f"Unsupported input format: {ext}")

    if ext in {".md", ".markdown"}:
        meta = normalize_obsidian_markdown(src, out_dir, vault, title, author, cover)
    else:
        meta = metadata_for_non_md(src, out_dir, title, author, cover, vault)
    work_src = meta.work_src or src
    dst = out_dir / f"{slugify(meta.title)}.{fmt}"
    run_pandoc(work_src, dst, meta, [src.parent, vault, vault / "sources" / "attachments", out_dir], toc=toc)
    return dst, meta


def send_email(attachment: Path, subject: str, smtp_host: str, smtp_port: int, sender: str, receiver: str) -> str:
    password = os.getenv("KINDLE_SMTP_PASSWORD") or os.getenv("QQ_SMTP_AUTH_CODE")
    if not password:
        raise RuntimeError("Missing SMTP password. Set QQ_SMTP_AUTH_CODE or KINDLE_SMTP_PASSWORD to QQ Mail authorization code.")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Subject"] = subject
    msg.set_content("Sent by Hermes send-to-kindle skill.")
    ctype, encoding = mimetypes.guess_type(str(attachment))
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    msg.add_attachment(attachment.read_bytes(), maintype=maintype, subtype=subtype, filename=attachment.name)
    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=60) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
    return f"sent via {smtp_host}:{smtp_port} from {sender} to {receiver}"


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return str(path.stat().st_size)


def main() -> int:
    load_env_file()
    parser = argparse.ArgumentParser(description="Send Obsidian/local document to Kindle")
    parser.add_argument("input", help="Local path, Obsidian vault-relative path, or note title/search text")
    parser.add_argument("--send", action="store_true", help="Send email to Kindle after generating file")
    parser.add_argument("--format", default=os.getenv("KINDLE_DEFAULT_FORMAT", "epub"), choices=["epub", "pdf", "docx", "original"])
    parser.add_argument("--title", help="Override EPUB title")
    parser.add_argument("--author", help="Override EPUB author")
    parser.add_argument("--cover", default=os.getenv("KINDLE_COVER", "auto"), help="Cover path, auto, or none. Default: auto")
    parser.add_argument("--no-toc", action="store_true", help="Disable EPUB table of contents")
    parser.add_argument("--subject", default=os.getenv("KINDLE_EMAIL_SUBJECT", "Convert"), help="Email subject")
    parser.add_argument("--vault", default=os.getenv("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT))
    parser.add_argument("--out-dir", default=os.getenv("KINDLE_OUTPUT_DIR", DEFAULT_OUT))
    parser.add_argument("--smtp-host", default=os.getenv("KINDLE_SMTP_HOST", DEFAULT_SMTP_HOST))
    parser.add_argument("--smtp-port", type=int, default=int(os.getenv("KINDLE_SMTP_PORT", str(DEFAULT_SMTP_PORT))))
    parser.add_argument("--sender", default=os.getenv("KINDLE_FROM_EMAIL", DEFAULT_FROM))
    parser.add_argument("--receiver", default=os.getenv("KINDLE_EMAIL", DEFAULT_TO))
    args = parser.parse_args()

    vault = Path(args.vault).expanduser()
    date_dir = Path(args.out_dir).expanduser() / datetime.now().strftime("%Y-%m-%d")
    src = resolve_input(args.input, vault)
    fmt = args.format
    if fmt == "original" and src.suffix.lower().lstrip(".") in {"epub", "pdf"}:
        fmt = src.suffix.lower().lstrip(".")
    elif fmt == "original":
        fmt = "epub"
    output, meta = prepare_file(src, fmt, date_dir, vault, args.title, args.author, args.cover, toc=not args.no_toc)
    output = output.resolve()
    if not output.exists():
        raise RuntimeError(f"Output file was not created: {output}")

    print(f"source={src}")
    print(f"output={output}")
    print(f"size={human_size(output)}")
    print(f"title={meta.title}")
    print(f"author={meta.author}")
    if meta.cover:
        print(f"cover={meta.cover}")
    if meta.css:
        print(f"css={meta.css}")

    if args.send:
        status = send_email(output, args.subject, args.smtp_host, args.smtp_port, args.sender, args.receiver)
        print(f"send_status={status}")
    else:
        print("send_status=not sent (--send not specified)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error={exc}", file=sys.stderr)
        raise SystemExit(1)
