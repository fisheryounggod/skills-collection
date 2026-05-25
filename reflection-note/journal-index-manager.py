#!/usr/bin/env python3
"""
日记索引管理
维护每日日记文档的索引，用于查找和追加
"""

import sys
import json
import os
from datetime import datetime

INDEX_FILE = "/home/yxf/.openclaw/workspace/journal-index.json"

def load_index():
    """
    加载日记索引
    
    Returns:
        index: 索引字典 {date: doc_token}
    """
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    else:
        return {}

def save_index(index):
    """
    保存日记索引
    
    Args:
        index: 索引字典
    """
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

def find_today_journal(date=None):
    """
    查找今日日记
    
    Args:
        date: 日期字符串（YYYY-MM-DD），默认今天
    
    Returns:
        doc_token: 日记文档token，如果找不到则为None
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    index = load_index()
    return index.get(date)

def update_index(date, doc_token):
    """
    更新索引
    
    Args:
        date: 日期字符串
        doc_token: 文档token
    """
    index = load_index()
    index[date] = doc_token
    save_index(index)

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "find"
    
    if command == "find":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        doc_token = find_today_journal(date)
        
        if doc_token:
            print(json.dumps({"found": True, "doc_token": doc_token, "date": date}))
        else:
            print(json.dumps({"found": False, "date": date}))
    
    elif command == "update":
        date = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')
        doc_token = sys.argv[3] if len(sys.argv) > 3 else ""
        
        if date and doc_token:
            update_index(date, doc_token)
            print(json.dumps({"updated": True, "date": date, "doc_token": doc_token}))
        else:
            print(json.dumps({"error": "Missing date or doc_token"}))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}. Use 'find' or 'update'."}))

if __name__ == "__main__":
    main()
