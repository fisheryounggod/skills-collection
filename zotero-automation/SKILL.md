---
name: zotero-automation
description: This skill should be used when the user asks to "manage Zotero library", "add Zotero references", "search Zotero", "export citations from Zotero", "backup Zotero library", "organize Zotero collections", or mentions working with Zotero references/literature management. Automates Zotero library operations using pyzotero.
version: 0.1.0
---

# Zotero Automation

Automate Zotero reference library management using pyzotero. This skill provides tools and workflows for managing academic references, organizing collections, exporting citations, and backing up literature libraries.

## Prerequisites

Ensure pyzotero is installed and environment variables are configured:

```bash
pip install pyzotero
```

Required environment variables (already configured in `.zshrc`):
- `ZOTERO_USER_ID` - Zotero user ID
- `ZOTERO_API_KEY` - Zotero API key
- `ZOTERO_LOCAL` - Set to "false" for cloud library, "true" for local

## Core Workflows

### List and Search References

Use the bundled script to list or search items:

```bash
# List recent items (default 20)
~/.claude/skills/zotero-automation/scripts/zotero_manager.py list

# List with specific limit
~/.claude/skills/zotero-automation/scripts/zotero_manager.py list -n 50

# Search for specific papers
~/.claude/skills/zotero-automation/scripts/zotero_manager.py list -q "machine learning"

# List items in a specific collection
~/.claude/skills/zotero-automation/scripts/zotero_manager.py list -c <collection_key>
```

### Add New References

Add references using the CLI tool:

```bash
# Add a book
~/.claude/skills/zotero-automation/scripts/zotero_manager.py add book "Book Title" \
  --author "Author Name" \
  --year "2024"

# Add a journal article
~/.claude/skills/zotero-automation/scripts/zotero_manager.py add journalArticle \
  "Article Title" --author "Author Name" --year "2024" --doi "10.xxxx/xxxxx"
```

For programmatic access, use pyzotero directly in Python:

```python
from pyzotero import zotero
import os

zot = zotero.Zotero(
    os.getenv('ZOTERO_USER_ID'),
    'user',
    os.getenv('ZOTERO_API_KEY')
)

# Get template for item type
template = zot.item_template('journalArticle')
template['title'] = 'Your Paper Title'
template['date'] = '2024'
template['DOI'] = '10.xxxx/xxxxx'

# Create item
response = zot.create_items([template])
print(f"Created item with key: {response['successful']['0']['key']}")
```

### Update Existing Items

Update item metadata:

```bash
# Update item title
~/.claude/skills/zotero-automation/scripts/zotero_manager.py update <item_key> \
  --title "New Title"

# Update publication year
~/.claude/skills/zotero-automation/scripts/zotero_manager.py update <item_key> \
  --year "2025"
```

### Show Item Details

View complete item information:

```bash
~/.claude/skills/zotero-automation/scripts/zotero_manager.py show <item_key>
```

This displays:
- Item type and title
- All authors/creators
- Publication details
- Tags
- Associated collections

### Delete Items

Remove items from the library:

```bash
~/.claude/skills/zotero-automation/scripts/zotero_manager.py delete <item_key>
```

**Warning:** Deletion is permanent. Consider backing up before bulk operations.

### Export Citations

Export library or collections to BibTeX format:

```bash
# Export entire library to file
~/.claude/skills/zotero-automation/scripts/zotero_manager.py export -o references.bib

# Export specific collection
~/.claude/skills/zotero-automation/scripts/zotero_manager.py export \
  -c <collection_key> -o collection.bib

# Print to stdout
~/.claude/skills/zotero-automation/scripts/zotero_manager.py export
```

### Manage Collections

List all collections:

```bash
~/.claude/skills/zotero-automation/scripts/zotero_manager.py collections
```

Create new collections programmatically:

```python
from pyzotero import zotero
import os

zot = zotero.Zotero(
    os.getenv('ZOTERO_USER_ID'),
    'user',
    os.getenv('ZOTERO_API_KEY')
)

# Create collection
collection_data = {'name': 'Research Project 2024'}
response = zot.create_collection(collection_data)
print(f"Created collection: {response['data']['key']}")
```

Add items to collections:

```python
# Get collection and add item
collection = zot.get_collection(<collection_key>)
collection['data']['items'].append(<item_key>)
zot.update_collection(collection)
```

### Backup Library

Create timestamped backups of the entire library:

```bash
# Backup to default location (~/zotero-backup)
~/.claude/skills/zotero-automation/scripts/zotero_manager.py backup

# Backup to specific directory
~/.claude/skills/zotero-automation/scripts/zotero_manager.py backup -d /path/to/backup
```

Backups are saved as JSON with format: `zotero_backup_YYYYMMDD_HHMMSS.json`

## Common Use Cases

### Literature Review Workflow

1. Search for papers on a topic
2. Review item details
3. Organize into collections
4. Export to BibTeX for citation management

```bash
# Search papers
~/.claude/skills/zotero-automation/scripts/zotero_manager.py list -q "neural networks"

# View details
~/.claude/skills/zotero-automation/scripts/zotero_manager.py show <item_key>

# Export for LaTeX
~/.claude/skills/zotero-automation/scripts/zotero_manager.py export -o literature.bib
```

### Reference Organization

1. List all collections to understand structure
2. Create new collections for projects
3. Move items into appropriate collections

```bash
# List collections
~/.claude/skills/zotero-automation/scripts/zotero_manager.py collections

# Create collection and organize (use Python script for complex operations)
```

### Batch Operations

For batch operations, use Python directly with pyzotero:

```python
from pyzotero import zotero
import os

zot = zotero.Zotero(
    os.getenv('ZOTERO_USER_ID'),
    'user',
    os.getenv('ZOTERO_API_KEY')
)

# Get all items
all_items = zot.everything(zot.items())

# Filter and process
for item in all_items:
    if item['data']['itemType'] == 'journalArticle':
        # Process article
        pass
```

## Item Types Reference

Common Zotero item types for creating new entries:

- `book` - Books
- `journalArticle` - Journal articles
- `conferencePaper` - Conference papers
- `magazineArticle` - Magazine articles
- `newspaperArticle` - Newspaper articles
- `thesis` - Theses and dissertations
- `report` - Reports
- `webpage` - Web pages
- `document` - Generic documents

## Troubleshooting

### Import Error

If `pyzotero` is not found:

```bash
pip install pyzotero --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### Authentication Error

Verify environment variables are set:

```bash
echo $ZOTERO_USER_ID
echo $ZOTERO_API_KEY
```

Re-source `.zshrc` if needed:

```bash
source ~/.zshrc
```

### API Rate Limits

Zotero API has rate limits. For large operations, use `zot.everything(zot.items())` which handles pagination automatically, or add delays between requests.

## Additional Resources

### Reference Files

For advanced pyzotero usage and API details:
- **`references/pyzotero-api.md`** - Complete pyzotero API reference
- **`references/item-types.md`** - All Zotero item types and fields

### Examples

Working examples in `examples/`:
- **`examples/batch_operations.py`** - Batch update and organization
- **`examples/citation_export.py`** - Custom export formats

### Scripts

Utility scripts in `scripts/`:
- **`scripts/zotero_manager.py`** - Main CLI tool for all operations
