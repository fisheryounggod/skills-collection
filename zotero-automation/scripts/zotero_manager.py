#!/usr/bin/env python3
"""
Zotero Library Manager - Command-line tool for managing Zotero references
Requires pyzotero: pip install pyzotero

Environment variables:
- ZOTERO_USER_ID: Your Zotero user ID
- ZOTERO_API_KEY: Your Zotero API key
- ZOTERO_LOCAL: Set to "true" for local Zotero, "false" for cloud
"""

import os
import sys
import json
import argparse
from datetime import datetime

try:
    from pyzotero import zotero
except ImportError:
    print("Error: pyzotero not installed. Run: pip install pyzotero")
    sys.exit(1)


def get_zotero_client():
    """Initialize and return a Zotero client instance"""
    user_id = os.getenv('ZOTERO_USER_ID')
    api_key = os.getenv('ZOTERO_API_KEY')
    local = os.getenv('ZOTERO_LOCAL', 'false').lower() == 'true'

    if not user_id or not api_key:
        print("Error: ZOTERO_USER_ID and ZOTERO_API_KEY environment variables must be set")
        sys.exit(1)

    library_type = 'group' if local else 'user'
    return zotero.Zotero(user_id, library_type, api_key)


def list_items(limit=20, query=None, collection=None):
    """List items in Zotero library"""
    zot = get_zotero_client()

    kwargs = {}
    if query:
        kwargs['q'] = query
    if collection:
        kwargs['collection'] = collection

    items = zot.items(**kwargs)

    print(f"\n=== Zotero Library Items (showing {min(limit, len(items))} of {len(items)}) ===\n")

    for i, item in enumerate(items[:limit]):
        item_type = item.get('data', {}).get('itemType', 'unknown')
        title = item.get('data', {}).get('title', 'Untitled')
        creators = item.get('data', {}).get('creators', [])

        # Format creators
        if creators:
            author_names = [c.get('lastName', c.get('firstName', '')) for c in creators[:3]]
            authors = ', '.join(author_names)
            if len(creators) > 3:
                authors += ' et al.'
        else:
            authors = 'No author'

        item_key = item.get('data', {}).get('key', '')
        year = item.get('data', {}).get('date', '')[:4] if item.get('data', {}).get('date') else 'n.d.'

        print(f"[{i+1}] {item_type.upper()}: {title}")
        print(f"    Authors: {authors}")
        print(f"    Year: {year} | Key: {item_key}")
        print()

    return items


def search_items(query):
    """Search for items matching query"""
    return list_items(limit=50, query=query)


def add_item(item_type, title, **kwargs):
    """Add a new item to Zotero library"""
    zot = get_zotero_client()

    # Get template for item type
    template = zot.item_template(item_type)
    template['title'] = title

    # Add additional fields
    for key, value in kwargs.items():
        if value:
            template[key] = value

    # Create the item
    response = zot.create_items([template])

    print(f"✓ Item '{title}' added successfully!")
    print(f"  Item Key: {response.get('successful', {}).get('0', {}).get('key', 'N/A')}")

    return response


def update_item(item_key, **updates):
    """Update an existing item"""
    zot = get_zotero_client()

    item = zot.get_item(item_key)
    if not item:
        print(f"Error: Item with key '{item_key}' not found")
        return None

    for key, value in updates.items():
        if value:
            item[key] = value

    response = zot.update_item(item)
    print(f"✓ Item '{item_key}' updated successfully!")

    return response


def delete_item(item_key):
    """Delete an item from Zotero library"""
    zot = get_zotero_client()

    response = zot.delete_item(item_key)
    print(f"✓ Item '{item_key}' deleted successfully!")

    return response


def export_bibtex(output_file=None, collection=None):
    """Export library or collection to BibTeX format"""
    zot = get_zotero_client()

    kwargs = {}
    if collection:
        kwargs['collection'] = collection

    items = zot.items(**kwargs)
    bibtex = zot.export(items[:-1])  # Zotero export format

    if output_file:
        with open(output_file, 'w') as f:
            f.write(bibtex)
        print(f"✓ Exported {len(items)} items to {output_file}")
    else:
        print(bibtex)

    return bibtex


def list_collections():
    """List all collections in the library"""
    zot = get_zotero_client()

    collections = zot.collections()

    print("\n=== Zotero Collections ===\n")

    for col in collections:
        name = col.get('data', {}).get('name', 'Unnamed')
        key = col.get('data', {}).get('key', '')
        num_items = col.get('meta', {}).get('numItems', 0)

        print(f"📁 {name} (Key: {key})")
        print(f"   Items: {num_items}")
        print()

    return collections


def create_collection(name, parent=None):
    """Create a new collection"""
    zot = get_zotero_client()

    collection_data = {'name': name}
    if parent:
        collection_data['parent'] = parent

    response = zot.create_collection(collection_data)

    print(f"✓ Collection '{name}' created successfully!")

    return response


def add_to_collection(item_key, collection_key):
    """Add an item to a collection"""
    zot = get_zotero_client()

    # Get the collection
    collection = zot.get_collection(collection_key)

    # Add item to collection
    collection['data']['items'].append(item_key)
    zot.update_collection(collection)

    print(f"✓ Item '{item_key}' added to collection!")

    return True


def backup_library(output_dir=None):
    """Backup entire library to JSON file"""
    zot = get_zotero_client()

    if not output_dir:
        output_dir = os.path.expanduser('~/zotero-backup')

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(output_dir, f'zotero_backup_{timestamp}.json')

    # Get all items
    all_items = zot.everything(zot.items())

    backup_data = {
        'timestamp': timestamp,
        'total_items': len(all_items),
        'items': all_items
    }

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Library backed up to {backup_file}")
    print(f"  Total items: {len(all_items)}")

    return backup_file


def show_item_details(item_key):
    """Show detailed information about an item"""
    zot = get_zotero_client()

    item = zot.get_item(item_key)

    if not item:
        print(f"Error: Item with key '{item_key}' not found")
        return None

    print(f"\n=== Item Details ===\n")
    print(f"Type: {item.get('data', {}).get('itemType', 'unknown')}")
    print(f"Title: {item.get('data', {}).get('title', 'N/A')}")

    creators = item.get('data', {}).get('creators', [])
    if creators:
        print("\nAuthors:")
        for creator in creators:
            first = creator.get('firstName', '')
            last = creator.get('lastName', '')
            creator_type = creator.get('creatorType', 'author')
            print(f"  - {first} {last} ({creator_type})")

    # Print all fields
    data = item.get('data', {})
    for key, value in data.items():
        if key not in ['title', 'creators', 'itemType', 'key'] and value:
            print(f"{key}: {value}")

    # Show tags
    tags = item.get('data', {}).get('tags', [])
    if tags:
        print("\nTags:")
        for tag in tags:
            print(f"  - {tag.get('tag', '')}")

    # Show collections
    collections = item.get('data', {}).get('collections', [])
    if collections:
        print(f"\nIn collections: {', '.join(collections)}")

    return item


def main():
    parser = argparse.ArgumentParser(description='Zotero Library Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List items in library')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='Number of items to show')
    list_parser.add_argument('-q', '--query', help='Search query')
    list_parser.add_argument('-c', '--collection', help='Collection key')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add new item')
    add_parser.add_argument('type', help='Item type (book, article, etc.)')
    add_parser.add_argument('title', help='Item title')
    add_parser.add_argument('--author', help='Author name')
    add_parser.add_argument('--year', help='Publication year')
    add_parser.add_argument('--doi', help='DOI')
    add_parser.add_argument('--abstract', help='Abstract text')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update an item')
    update_parser.add_argument('key', help='Item key')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--year', help='New publication year')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an item')
    delete_parser.add_argument('key', help='Item key')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export to BibTeX')
    export_parser.add_argument('-o', '--output', help='Output file')
    export_parser.add_argument('-c', '--collection', help='Collection key')

    # Collections command
    subparsers.add_parser('collections', help='List collections')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup library')
    backup_parser.add_argument('-d', '--dir', help='Output directory')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show item details')
    show_parser.add_argument('key', help='Item key')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'list':
        list_items(args.limit, args.query, args.collection)
    elif args.command == 'add':
        add_item(args.type, args.title,
                creator=args.author,
                date=args.year,
                DOI=args.doi,
                abstractNote=args.abstract)
    elif args.command == 'update':
        updates = {}
        if args.title:
            updates['title'] = args.title
        if args.year:
            updates['date'] = args.year
        update_item(args.key, **updates)
    elif args.command == 'delete':
        delete_item(args.key)
    elif args.command == 'export':
        export_bibtex(args.output, args.collection)
    elif args.command == 'collections':
        list_collections()
    elif args.command == 'backup':
        backup_library(args.dir)
    elif args.command == 'show':
        show_item_details(args.key)


if __name__ == '__main__':
    main()
