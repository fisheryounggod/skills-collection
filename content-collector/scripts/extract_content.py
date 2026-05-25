#!/usr/bin/env python3
"""
平台检测与 Skill 路由
检测URL来源，返回推荐的skill和提取方式
"""

import sys
import json
import re
from urllib.parse import urlparse, parse_qs

# 平台映射配置
PLATFORMS = {
    "x.com": {
        "id": "twitter",
        "label": "X/Twitter",
        "skill": "x-tweet-fetcher",
        "fallback_skills": [],
        "note": "使用 x-tweet-fetcher skill 提取推文/文章内容"
    },
    "twitter.com": {
        "id": "twitter",
        "label": "X/Twitter",
        "skill": "x-tweet-fetcher",
        "fallback_skills": [],
        "note": "使用 x-tweet-fetcher skill 提取推文/文章内容"
    },
    "mp.weixin.qq.com": {
        "id": "wechat_mp",
        "label": "微信公众号",
        "skill": "web-content-fetcher",
        "fallback_skills": ["defuddle"],
        "note": "使用 web-content-fetcher skill (Scrapling) 抓取公众号文章",
        "scrapling_command": "scrapling {url}",
        "selectors": {
            "title": "#activity-name",
            "author": "#js_name",
            "content": "#js_content",
            "time": "#publish_time"
        }
    },
    "okjike.com": {
        "id": "jike",
        "label": "即刻",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取即刻内容",
        "selectors": {
            "author": 'meta[property="og:title"]',
            "content": 'meta[property="og:description"]',
            "time": "time"
        }
    },
    "jike.cn": {
        "id": "jike",
        "label": "即刻",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取即刻内容"
    },
    "reddit.com": {
        "id": "reddit",
        "label": "Reddit",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取 Reddit 内容，或访问 {url}.json 获取结构化数据"
    },
    "news.ycombinator.com": {
        "id": "hackernews",
        "label": "Hacker News",
        "skill": "defuddle",
        "fallback_skills": [],
        "note": "使用 defuddle skill 提取 Hacker News 内容"
    },
    "zhihu.com": {
        "id": "zhihu",
        "label": "知乎",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取知乎内容"
    },
    "bilibili.com": {
        "id": "bilibili",
        "label": "Bilibili",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取 Bilibili 内容"
    },
    "b23.tv": {
        "id": "bilibili",
        "label": "Bilibili",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取 Bilibili 内容"
    },
}


def normalize_url(url):
    """标准化URL，去除追踪参数"""
    parsed = urlparse(url)
    
    # 追踪参数列表
    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'source'
    }
    
    # 过滤追踪参数
    query_params = parse_qs(parsed.query)
    filtered_params = {
        k: v for k, v in query_params.items()
        if k not in tracking_params
    }
    
    # 重建URL
    from urllib.parse import urlencode
    normalized = parsed._replace(query=urlencode(filtered_params, doseq=True))
    return normalized.geturl()


def detect_platform(url):
    """检测URL平台"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # 移除www前缀
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # 精确匹配
    if domain in PLATFORMS:
        return PLATFORMS[domain]
    
    # 域名匹配
    for platform_domain, config in PLATFORMS.items():
        if domain == platform_domain or domain.endswith('.' + platform_domain):
            return config
    
    # 默认使用 defuddle
    return {
        "id": "generic",
        "label": "通用网页",
        "skill": "defuddle",
        "fallback_skills": ["baoyu-url-to-markdown"],
        "note": "使用 defuddle skill 提取通用网页内容"
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 extract_content.py <url>"
        }))
        sys.exit(1)
    
    url = sys.argv[1]
    normalized_url = normalize_url(url)
    platform = detect_platform(url)
    
    result = {
        "platform_id": platform["id"],
        "platform_label": platform["label"],
        "url": normalized_url,
        "original_url": url,
        "skill": platform["skill"],
        "fallback_skills": platform.get("fallback_skills", []),
        "note": platform["note"]
    }
    
    # 添加额外信息
    if "scrapling_command" in platform:
        result["scrapling_command"] = platform["scrapling_command"].format(url=normalized_url)
    
    if "selectors" in platform:
        result["selectors"] = platform["selectors"]
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
