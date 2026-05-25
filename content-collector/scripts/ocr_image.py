#!/usr/bin/env python3
"""
图片OCR识别
识别图片中的文字，提取URL
"""

import sys
import os
import re


def ocr_with_tesseract(image_path):
    """使用tesseract进行OCR"""
    try:
        import pytesseract
        from PIL import Image
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        return text
    except ImportError:
        return None
    except Exception as e:
        return f"OCR Error: {e}"


def extract_urls(text):
    """从文本中提取URL"""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    return urls


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 ocr_image.py <image_path> [--external]"
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    use_external = "--external" in sys.argv
    
    if not os.path.exists(image_path):
        print(json.dumps({
            "error": f"Image file not found: {image_path}"
        }))
        sys.exit(1)
    
    result = {
        "image_path": image_path,
        "success": False,
        "text": "",
        "urls": [],
        "message": ""
    }
    
    if use_external:
        result["message"] = "请使用外部OCR服务识别此图片"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # 尝试本地OCR
    ocr_result = ocr_with_tesseract(image_path)
    
    if ocr_result is None:
        result["message"] = "本地OCR不可用（未安装pytesseract或pillow），请使用--external参数调用外部OCR服务"
    elif ocr_result.startswith("OCR Error"):
        result["message"] = ocr_result
    else:
        result["success"] = True
        result["text"] = ocr_result
        result["urls"] = extract_urls(ocr_result)
        result["message"] = f"OCR成功，识别到{len(result['urls'])}个URL"
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
