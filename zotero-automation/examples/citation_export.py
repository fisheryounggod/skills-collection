#!/usr/bin/env python3
"""
Custom citation export examples
Export Zotero library to various formats beyond BibTeX
"""

import os
import json
import csv
from pyzotero import zotero


def export_to_json(output_file='references.json'):
    """Export library to JSON format"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.everything(zot.items())

    # Simplify format for export
    export_data = []
    for item in items:
        data = item.get('data', {})

        # Extract authors
        creators = data.get('creators', [])
        authors = []
        for creator in creators:
            if creator.get('creatorType') == 'author':
                first = creator.get('firstName', '')
                last = creator.get('lastName', '')
                authors.append(f"{first} {last}".strip())

        export_data.append({
            'key': data.get('key', ''),
            'type': data.get('itemType', ''),
            'title': data.get('title', ''),
            'authors': authors,
            'year': data.get('date', '')[:4] if data.get('date') else '',
            'doi': data.get('DOI', ''),
            'url': data.get('url', ''),
            'tags': [t.get('tag', '') for t in data.get('tags', [])]
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Exported {len(export_data)} items to {output_file}")
    return export_data


def export_to_csv(output_file='references.csv'):
    """Export library to CSV format"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.everything(zot.items())

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Key', 'Type', 'Title', 'Authors', 'Year', 'DOI', 'URL', 'Tags'])

        for item in items:
            data = item.get('data', {})

            # Format authors
            creators = data.get('creators', [])
            authors = '; '.join([
                f"{c.get('firstName', '')} {c.get('lastName', '')}".strip()
                for c in creators[:5]
            ])

            # Format tags
            tags = '; '.join([t.get('tag', '') for t in data.get('tags', [])])

            writer.writerow([
                data.get('key', ''),
                data.get('itemType', ''),
                data.get('title', ''),
                authors,
                data.get('date', '')[:4] if data.get('date') else '',
                data.get('DOI', ''),
                data.get('url', ''),
                tags
            ])

    print(f"✓ Exported {len(items)} items to {output_file}")


def export_markdown_reading_list(output_file='reading_list.md'):
    """Export library as Markdown reading list"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.everything(zot.items())

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Reading List\n\n")

        for item in items:
            data = item.get('data', {})

            # Format citation
            title = data.get('title', 'Untitled')

            creators = data.get('creators', [])
            if creators:
                author = f"{creators[0].get('lastName', creators[0].get('firstName', ''))}"
                if len(creators) > 1:
                    author += f" et al."
            else:
                author = "Unknown"

            year = data.get('date', '')[:4] if data.get('date') else 'n.d.'
            doi = data.get('DOI', '')

            f.write(f"## {title}\n\n")
            f.write(f"**Authors:** {author}  \n")
            f.write(f"**Year:** {year}  \n")

            if doi:
                f.write(f"**DOI:** [{doi}](https://doi.org/{doi})  \n")

            url = data.get('url', '')
            if url:
                f.write(f"**URL:** [Link]({url})  \n")

            # Tags
            tags = [t.get('tag', '') for t in data.get('tags', [])]
            if tags:
                f.write(f"**Tags:** {', '.join(tags)}  \n")

            f.write("\n---\n\n")

    print(f"✓ Exported reading list to {output_file}")


if __name__ == '__main__':
    export_to_json()
    export_to_csv()
    export_markdown_reading_list()
