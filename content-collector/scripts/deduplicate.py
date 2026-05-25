#!/usr/bin/env python3
"""
URL去重检查
检查URL是否已收藏（本地缓存 + 文档检查）
"""

import sys
import json
import os
from urllib.parse import urlparse
from datetime import datetime

CACHE_FILE = ".cache/collected_urls.json"


def load_cache():
    """加载本地缓存"""
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load cache: {e}", file=sys.stderr)
        return {}


def save_cache(cache):
    """保存本地缓存"""
    # 确保目录存在
    cache_dir = os.path.dirname(CACHE_FILE)
    if cache_dir and not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save cache: {e}", file=sys.stderr)


def normalize_url(url):
    """标准化URL"""
    parsed = urlparse(url)
    return parsed.netloc + parsed.path


def check_duplicate(url, cache):
    """检查URL是否重复"""
    normalized = normalize_url(url)
    
    # 检查本地缓存
    if normalized in cache:
        cache[normalized]["last_checked"] = datetime.now().isoformat()
        cache[normalized]["check_count"] = cache[normalized].get("check_count", 0) + 1
        return True, cache[normalized]
    
    # 添加到缓存
    cache[normalized] = {
        "original_url": url,
        "normalized": normalized,
        "date": datetime.now().isoformat(),
        "last_checked": datetime.now().isoformat(),
        "check_count": 1
    }
    
    return False, None


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 deduplicate.py <url> [--check-only]"
        }))
        sys.exit(1)
    
    url = sys.argv[1]
    check_only = "--check-only" in sys.argv
    
    cache = load_cache()
    
    is_duplicate, metadata = check_duplicate(url, cache)
    
    if not check_only:
        save_cache(cache)
    
    result = {
        "url": url,
        "is_duplicate": is_duplicate,
        "timestamp": datetime.now().isoformat()
    }
    
    if is_duplicate:
        result["metadata"] = metadata
        result["message"] = "URL已存在于缓存中"
    else:
        result["message"] = "URL首次出现"
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
