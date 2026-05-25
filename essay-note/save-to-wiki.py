#!/usr/bin/env python3
"""
随笔保存器
将格式化的随笔保存到飞书知识库
"""

import sys
import json
import subprocess

def save_to_feishu_doc(md_content):
    """
    保存随笔到飞书文档
    
    Args:
        md_content: markdown格式的随笔内容
    
    Returns:
        result: 保存结果（文档链接）
    """
    # 提取第一行作为标题（去掉 # 💡 前缀）
    lines = md_content.split('\n')
    title = lines[0].replace('# 💡 ', '').strip()
    
    try:
        # 使用feishu_doc创建文档
        result = subprocess.run(
            ["feishu_doc", "create",
             "--title", title,
             "--content", md_content,
             "--folder_token", "QXmwfrCerld1a7d0qVUczfC7nae"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # 提取doc_token和URL
            output = result.stdout
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
        print(json.dumps({"error": "Usage: python save-to-wiki.py '<md_content>'"}))
        sys.exit(1)
    
    md_content = sys.argv[1]
    
    result = save_to_feishu_doc(md_content)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
