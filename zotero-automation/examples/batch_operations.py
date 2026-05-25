#!/usr/bin/env python3
"""
Examples of batch operations with Zotero library
Useful for organizing and updating multiple references at once
"""

import os
from pyzotero import zotero


def batch_tag_items(query, new_tag):
    """Add a tag to all items matching a search query"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.items(q=query)

    for item in items:
        item_data = item.get('data', {})
        tags = item_data.get('tags', [])

        # Add new tag if not present
        if not any(t.get('tag') == new_tag for t in tags):
            tags.append({'tag': new_tag})
            item_data['tags'] = tags
            zot.update_item(item)
            print(f"✓ Tagged '{item_data.get('title', 'Untitled')}' with '{new_tag}'")


def batch_update_year(old_year, new_year):
    """Update publication year for all items with old_year"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.everything(zot.items())

    updated = 0
    for item in items:
        item_data = item.get('data', {})
        date = item_data.get('date', '')

        if date.startswith(old_year):
            item_data['date'] = date.replace(old_year, new_year, 1)
            zot.update_item(item)
            updated += 1
            print(f"✓ Updated '{item_data.get('title', 'Untitled')}'")

    print(f"\nTotal updated: {updated} items")


def find_duplicates():
    """Find potential duplicate items based on title"""
    zot = zotero.Zotero(
        os.getenv('ZOTERO_USER_ID'),
        'user',
        os.getenv('ZOTERO_API_KEY')
    )

    items = zot.everything(zot.items())
    titles = {}

    for item in items:
        title = item.get('data', {}).get('title', '').lower().strip()
        item_key = item.get('data', {}).get('key', '')

        if title:
            if title not in titles:
                titles[title] = []
            titles[title].append(item_key)

    # Show duplicates
    print("\n=== Potential Duplicates ===\n")
    for title, keys in titles.items():
        if len(keys) > 1:
            print(f"'{title}' ({len(keys)} items):")
            for key in keys:
                print(f"  - {key}")
            print()


if __name__ == '__main__':
    # Example usage
    # batch_tag_items('machine learning', 'ML-Review-2024')
    # batch_update_year('2023', '2024')
    find_duplicates()
