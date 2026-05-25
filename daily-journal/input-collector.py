#!/usr/bin/env python3
"""
日记输入收集器
收集用户输入，不中断，完成后询问"还有要记的吗？"
"""

import sys
import json
from datetime import datetime

def collect_entries(input_text, existing_entries=None):
    """
    收集用户输入，追加到现有条目
    
    Args:
        input_text: 用户的输入文本
        existing_entries: 已有的条目列表
    
    Returns:
        entries: 更新后的条目列表
        has_more: 是否有更多内容
    """
    if existing_entries is None:
        existing_entries = []
    
    # 分割用户输入为条目（按换行或句号）
    entries = []
    lines = input_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.endswith('？') and not line.endswith('?'):
            # 如果不是问题，视为日记条目
            entries.append(line)
    
    # 追加到现有条目
    all_entries = existing_entries + entries
    
    # 检查是否需要询问更多
    # 简单的启发式：如果输入不以"就这样"、"没有了"等结束，则询问
    end_markers = ['就这样', '没有了', '完了', '结束']
    has_more = not any(marker in input_text for marker in end_markers)
    
    return all_entries, has_more

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python input-collector.py '<input_text>'"}))
        sys.exit(1)
    
    input_text = sys.argv[1]
    
    # 从标准输入读取现有条目（可选）
    import json
    try:
        existing = json.load(sys.stdin) if sys.stdin.isatty() is False else []
    except:
        existing = []
    
    entries, has_more = collect_entries(input_text, existing)
    
    result = {
        "entries": entries,
        "has_more": has_more,
        "count": len(entries)
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
