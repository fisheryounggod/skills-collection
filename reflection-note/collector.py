#!/usr/bin/env python3
"""
反思输入收集器
收集用户的反思内容
"""

import sys
import json
import re
from datetime import datetime

def collect_reflection(user_input):
    """
    收集反思内容
    
    Args:
        user_input: 用户输入文本
    
    Returns:
        reflection: 反思内容
    """
    # 去掉触发词
    triggers = ['记一下反思：', '反思一下：', '我的反思是', '反思：']
    reflection = user_input
    
    for trigger in triggers:
        reflection = reflection.replace(trigger, '', 1)
    
    # 去掉引号（如果有）
    reflection = reflection.strip().strip('"').strip('""')
    
    return reflection

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python collector.py '<user_input>'"}))
        sys.exit(1)
    
    user_input = sys.argv[1]
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 收集反思内容
    reflection = collect_reflection(user_input)
    
    result = {
        "time": current_time,
        "reflection": reflection
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
