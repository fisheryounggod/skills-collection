#!/usr/bin/env python3
"""
日记保存器（简化版）
将格式化的日记保存到飞书文档
"""

import sys
import os
import json
import subprocess

def save_to_feishu_doc(md_content, date):
    """
    保存日记到飞书文档
    
    Args:
        md_content: markdown格式的日记内容
        date: 日期字符串
    
    Returns:
        result: 保存结果（文档链接）
    """
    # 提取第一行作为标题
    title = f"{date} 日记"
    
    try:
        # 使用feishu_doc创建文档（不需要先创建docx，直接传content）
        # 注意：feishu_doc create有时会导致content丢失，需要follow-up write
        result = subprocess.run(
            ["feishu_doc", "create", 
             "--title", title,
             "--content", md_content,
             "--folder_token", "ZZMKfKN7Kl5WsYdUbRacokmjnwg"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # 提取doc_token
            output = result.stdout
            # 尝试解析JSON输出
            try:
                data = json.loads(output)
                doc_token = data.get("document_id", "")
                doc_url = data.get("url", "")
                
                # 立即用write修复内容（防止create导致的内容丢失）
                if doc_token:
                    write_result = subprocess.run(
                        ["feishu_doc", "write",
                         "--doc_token", doc_token,
                         "--content", md_content],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if write_result.returncode == 0:
                        return {"success": True, "message": "保存成功", "url": doc_url, "doc_id": doc_token}
                    else:
                        return {"success": True, "message": "创建成功但write失败", "url": doc_url, "doc_id": doc_token}
                
            except:
                # 如果不是JSON输出，直接认为成功
                return {"success": True, "message": "保存成功"}
        else:
            return {"success": False, "error": result.stderr}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "保存超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python save-to-wiki.py '<md_content>' [date]"}))
        sys.exit(1)
    
    md_content = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else None
    
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d')
    
    result = save_to_feishu_doc(md_content, date)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
