---
name: marp-slide-generator
description: Generates Marp-formatted presentation slides from PDF documents or text content. Use this skill when the user wants to create presentation slides, PPTs, or slide decks from existing documents.
---

# Marp Slide Generator

This skill helps you generate [Marp](https://marpit.marp.app/)-formatted Markdown presentations from source documents (usually PDFs).

## Workflow

1.  **Extract Content**
    If the source is a PDF, use the bundled `extract_pdf_text.py` script to get the raw text.

    ```bash
    python3 /Users/mac/.gemini/antigravity/skills/marp-slide-generator/scripts/extract_pdf_text.py <input_pdf_path> <output_txt_path>
    ```

    *Note: Always use absolute paths.*

2.  **Plan Structure**
    Read the extracted text. Create an outline for the presentation. A typical chapter presentation should have 10-15 slides.
    - Title Slide
    - Learning Objectives / Agenda
    - Main Content Sections (break down by headers)
    - Conclusion / Summary

3.  **Generate Markdown**
    Write the Markdown file. Use the `assets/template.md` as a reference or starting point.
    
    **Key Syntax**:
    - `---` separates slides.
    - `#` for slide titles.
    - `*` or `-` for bullet points.
    - `<!-- _class: lead -->` for title/section slides.

    **Example Header**:
    ```yaml
    ---
    marp: true
    theme: default
    paginate: true
    header: "Presentation Title"
    footer: "Footer Text"
    ---
    ```

## Guidelines

- **Conciseness**: Slides should not be walls of text. Summarize key points.
- **Visuals**: Use bullet points and appropriate hierarchy.
- **Equations**: LaTeX math is supported (e.g., `$E = mc^2$`).
- **Images**: If extracting images, link them using standard markdown syntax `![alt](path)`.

## Resources

- **Script**: `scripts/extract_pdf_text.py` - Extracts text from PDFs using `pypdf`.
- **Template**: `assets/template.md` - Basic Marp slide template.
