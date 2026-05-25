#!/usr/bin/env python3
"""
反思保存器（追加到日记，使用索引）
将反思内容追加到日记的"## 反思"部分
"""

import sys
import json
import subprocess

def append_reflection_to_journal(md_reflection, date):
    """
    将反思内容追加到日记的"## 反思"部分
    
    Args:
        md_reflection: markdown格式的反思内容
        date: 日期字符串（YYYY-MM-DD）
    
    Returns:
        result: 保存结果
    """
    title = f"{date} 日记"
    
    # 查找现有日记
    find_result = subprocess.run(
        ["python3", "/home/yxf/.openclaw/workspace/skills/reflection-note/journal-index-manager.py", "find", date],
        capture_output=True,
        text=True
    )
    
    existing_doc_token = None
    existing_content = ""
    
    if find_result.returncode == 0:
        try:
            find_data = json.loads(find_result.stdout)
            if find_data.get("found"):
                existing_doc_token = find_data.get("doc_token", "")
                
                # 读取现有日记内容
                read_result = subprocess.run(
                    ["feishu_doc", "read",
                     "--doc_token", existing_doc_token],
                    capture_output=True,
                    text=True
                )
                
                if read_result.returncode == 0:
                    existing_content = read_result.stdout
        except:
            pass
    
    # 追加反思内容
    if existing_content and "## 反思" in existing_content:
        # 日记已有反思部分，追加内容
        lines = existing_content.split('\n')
        new_content = []
        in_reflection_section = False
        reflection_added = False
        
        for line in lines:
            if line.strip() == "## 反思":
                in_reflection_section = True
                new_content.append(line)
                # 在反思部分后追加新的反思
                reflection_lines = md_reflection.split('\n')
                for ref_line in reflection_lines:
                    if ref_line.strip():
                        new_content.append(ref_line)
                reflection_added = True
            elif line.strip().startswith("## ") and in_reflection_section:
                # 遇到下一个section，退出反思section
                in_reflection_section = False
                new_content.append(line)
            else:
                new_content.append(line)
        
        if not reflection_added:
            # 没有找到反思section或没追加上，直接追加到末尾
            new_content = existing_content + "\n" + md_reflection
    elif existing_content:
        # 日记存在但没有反思section，追加
        new_content = existing_content + "\n" + md_reflection
    else:
        # 日记不存在，创建新日记
        new_content = f"# 📅 {date} 日记\n\n{md_reflection}"
    
    # 保存
    if existing_doc_token:
        # 更新现有日记
        result = subprocess.run(
            ["feishu_doc", "write",
             "--doc_token", existing_doc_token,
             "--content", new_content],
            capture_output=True,
            text=True,
            timeout=30
        )
    else:
        # 创建新日记
        result = subprocess.run(
            ["feishu_doc", "create",
             "--title", title,
             "--content", new_content,
             "--folder_token", "ZZMKfKN7Kl5WsYdUbRacokmjnwg"],
            capture_output=True,
            text=True,
            timeout=30
        )
    
    # 处理结果
    if result.returncode == 0:
        output = result.stdout
        
        # 尝试解析JSON（如果输出是JSON）
        try:
            data = json.loads(output)
            doc_token = data.get("document_id", "")
            doc_url = data.get("url", "")
            
            # 更新索引
            if doc_token and not existing_doc_token:
                update_result = subprocess.run(
                    ["python3", "/home/yxf/.openclaw/workspace/skills/reflection-note/journal-index-manager.py", "update", date, doc_token],
                    capture_output=True,
                    text=True
                )
            
            return {"success": True, "message": "保存成功", "url": doc_url if doc_url else "", "doc_id": doc_token}
        except:
            # 如果不是JSON输出，直接认为成功
            return {"success": True, "message": "保存成功（非JSON输出）"}
    else:
        return {"success": False, "error": result.stderr}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python save-to-journal.py '<md_reflection>' [date]"}))
        sys.exit(1)
    
    md_reflection = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else None
    
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d')
    
    result = append_reflection_to_journal(md_reflection, date)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
