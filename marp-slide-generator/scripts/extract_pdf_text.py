import sys
import argparse
from pypdf import PdfReader

def extract_text(pdf_path, output_txt_path):
    """
    Extracts text from a PDF file and saves it to a text file.
    """
    try:
        reader = PdfReader(pdf_path)
        text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(f"--- Page {i+1} ---\n{page_text}\n")
            else:
                text.append(f"--- Page {i+1} ---\n[No text extracted]\n")
        
        full_text = "\n".join(text)
        
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"Successfully extracted text to {output_txt_path}")
        
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from a PDF file.")
    parser.add_argument("input_pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_txt_path", help="Path to the output text file")
    
    args = parser.parse_args()
    
    extract_text(args.input_pdf_path, args.output_txt_path)
