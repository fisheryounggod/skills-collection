# Pyzotero API Reference

Complete reference for pyzotero Python library.

## Initialization

```python
from pyzotero import zotero

# For user library
zot = zotero.Zotero(library_id, 'user', api_key)

# For group library
zot = zotero.Zotero(library_id, 'group', api_key)
```

## Core Methods

### Item Operations

#### `items(**kwargs)`
Retrieve items from the library with optional filtering.

**Parameters:**
- `limit` (int) - Maximum number of results
- `start` (int) - Starting index for pagination
- `q` (str) - Search query string
- `collection` (str) - Collection key to filter by
- `tag` (str) - Tag to filter by

**Returns:** List of item objects

```python
# Get all items (with pagination)
items = zot.items()

# Search items
results = zot.items(q='machine learning')

# Filter by collection
collection_items = zot.items(collection='ABC123')

# With limit
recent = zot.items(limit=10)
```

#### `get_item(item_key)`
Retrieve a specific item by its key.

```python
item = zot.get_item('ABCD1234')
```

#### `create_items(items)`
Create one or more new items.

```python
# Single item
template = zot.item_template('book')
template['title'] = 'My Book'
response = zot.create_items([template])

# Multiple items
items = [template1, template2]
response = zot.create_items(items)
```

#### `update_item(item)`
Update an existing item.

```python
item = zot.get_item('ABCD1234')
item['data']['title'] = 'Updated Title'
zot.update_item(item)
```

#### `delete_item(item_key)`
Delete an item from the library.

```python
zot.delete_item('ABCD1234')
```

#### `everything(items)`
Helper to handle pagination and retrieve all items.

```python
# Get all items without manual pagination
all_items = zot.everything(zot.items())
```

### Template Operations

#### `item_template(item_type)`
Get a blank template for a specific item type.

```python
book_template = zot.item_template('book')
# Returns dict with required fields for book type
```

**Common item types:**
- `book`
- `journalArticle`
- `conferencePaper`
- `magazineArticle`
- `newspaperArticle`
- `thesis`
- `report`
- `webpage`
- `document`

### Collection Operations

#### `collections()`
Retrieve all collections.

```python
collections = zot.collections()
```

#### `get_collection(collection_key)`
Retrieve a specific collection.

```python
collection = zot.get_collection('XYZ789')
```

#### `create_collection(collection_data)`
Create a new collection.

```python
collection_data = {
    'name': 'My Research',
    'parent': 'PARENT_KEY'  # Optional
}
response = zot.create_collection(collection_data)
```

#### `update_collection(collection)`
Update an existing collection.

```python
collection = zot.get_collection('XYZ789')
collection['data']['name'] = 'Updated Name'
zot.update_collection(collection)
```

### Tag Operations

#### `tags()`
Retrieve all tags in the library.

```python
tags = zot.tags()
```

#### `add_items_to_collection(item_keys, collection_key)`
Add items to a collection.

```python
zot.add_items_to_collection(['KEY1', 'KEY2'], 'COLL_KEY')
```

### Export Operations

#### `export(items)`
Export items to BibTeX format.

```python
items = zot.items()
bibtex = zot.export(items[:-1])  # Exclude last item
```

### Attachment Operations

#### `attachment(item_key)`
Retrieve attachment for an item.

```python
attachment = zot.attachment('ITEM_KEY')
```

#### `attachment_simple(item_key, filename)`
Get attachment as file.

```python
file_data = zot.attachment_simple('ITEM_KEY', 'paper.pdf')
```

## Item Data Structure

All items follow this structure:

```python
{
    'key': 'ABCD1234',
    'version': 1234,
    'library': {'type': 'user', 'id': 123456},
    'links': {...},
    'meta': {
        'created': '2024-01-01T00:00:00Z',
        'modified': '2024-01-01T00:00:00Z',
        'numItems': 1
    },
    'data': {
        'key': 'ABCD1234',
        'version': 1234,
        'itemType': 'journalArticle',
        'title': 'Paper Title',
        'creators': [
            {
                'creatorType': 'author',
                'firstName': 'John',
                'lastName': 'Doe'
            }
        ],
        'date': '2024',
        'DOI': '10.xxxx/xxxxx',
        'url': 'https://...',
        'tags': [{'tag': 'machine-learning'}],
        'collections': ['COLL1', 'COLL2'],
        'relations': {},
        'abstractNote': 'Abstract text...'
    }
}
```

## Creator Types

Common creator types:
- `author` - Primary author
- `editor` - Editor
- `translator` - Translator
- `contributor` - Contributor

## Error Handling

```python
from pyzotero import zotero
from requests.exceptions import HTTPError

try:
    item = zot.get_item('INVALID_KEY')
except HTTPError as e:
    print(f"HTTP Error: {e}")
except zotero.ZoteroError as e:
    print(f"Zotero Error: {e}")
```

## Rate Limiting

Zotero API has rate limits:
- Standard requests: Use reasonable delays
- Large operations: Use `everything()` for automatic handling
- Batch operations: Process in chunks

```python
import time

for item in large_list:
    zot.update_item(item)
    time.sleep(0.5)  # Avoid rate limits
```

## Best Practices

1. **Use `everything()` for large datasets** - Handles pagination automatically
2. **Cache item data** - Reduce API calls
3. **Batch operations** - Group multiple changes
4. **Handle errors gracefully** - Catch and log exceptions
5. **Respect rate limits** - Add delays for bulk operations
