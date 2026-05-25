#!/usr/bin/env python3
"""
随笔输入收集器
收集用户想法，不追问，直接整理
"""

import sys
import json
import re
from datetime import datetime

def extract_keywords(user_input):
    """
    提取主题关键词（简化的启发式方法）
    
    Args:
        user_input: 用户输入文本
    
    Returns:
        keywords: 关键词列表
    """
    # 简单的关键词提取：查找出现的高频词或特殊短语
    # 去掉常用词
    stop_words = {'我', '的', '了', '是', '在', '和', '有', '就', '不', '也', '都', '这', '那', '一个', '一个', '什么', '怎么'}
    
    words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', user_input)
    keywords = [w for w in words if w not in stop_words]
    
    # 取前3个作为标签
    tags = ['#' + w for w in keywords[:3]]
    
    # 提取主题关键词（第一个有意义的词或短语）
    if keywords:
        topic = keywords[0]
    else:
        topic = "随笔"
    
    return topic, tags

def extract_core_ideas(user_input):
    """
    提炼核心想法（1-3句）
    
    Args:
        user_input: 用户输入文本
    
    Returns:
        ideas: 核心观点列表
    """
    # 简单的句子分割
    sentences = re.split(r'[。！？，,;\n]', user_input)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 去掉太短的句子（少于5个字）
    ideas = [s for s in sentences if len(s) >= 5]
    
    # 取前3句
    return ideas[:3]

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python collector.py '<user_input>'"}))
        sys.exit(1)
    
    user_input = sys.argv[1]
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 提取关键词
    topic, tags = extract_keywords(user_input)
    
    # 提炼核心想法
    core_ideas = extract_core_ideas(user_input)
    
    result = {
        "topic": topic,
        "record_time": current_time,
        "core_ideas": core_ideas,
        "original": user_input,
        "tags": tags
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
