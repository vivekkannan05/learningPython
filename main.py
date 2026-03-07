"""
PDF Reader Project
Reads a PDF file from the /content folder and writes its text content to output.txt
"""

import os
from pathlib import Path
from PyPDF2 import PdfReader


def get_content_folder() -> Path:
    """Get the content folder path."""
    return Path(__file__).parent / "content"


def read_pdf_to_text(pdf_filename: str) -> None:
    """
    Read a PDF file from the content folder and write its text to output.txt.
    
    Args:
        pdf_filename: Name of the PDF file to read (e.g., "document.pdf")
    
    Raises:
        FileNotFoundError: If content folder or PDF file doesn't exist
        PermissionError: If unable to write to output file
        Exception: For other PDF reading errors
    """
    content_folder = get_content_folder()
    pdf_path = content_folder / pdf_filename
    output_path = content_folder / "output.txt"
    
    # Check if content folder exists
    if not content_folder.exists():
        raise FileNotFoundError(
            f"Content folder does not exist: {content_folder}\n"
            "Please create the 'content' folder in the project directory."
        )
    
    # Check if PDF file exists
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}\n"
            "Please place a PDF file in the 'content' folder."
        )
    
    # Check if PDF file is actually a PDF
    if not pdf_filename.lower().endswith('.pdf'):
        raise ValueError(f"File '{pdf_filename}' is not a PDF file.")
    
    try:
        # Read PDF and extract text
        print(f"Reading PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        
        text_content = []
        total_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages, 1):
            print(f"Processing page {i}/{total_pages}...")
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"--- Page {i} ---\n{page_text}\n")
            else:
                text_content.append(f"--- Page {i} ---\n[No extractable text on this page]\n")
        
        full_text = "\n".join(text_content)
        
        # Write to output file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"Successfully wrote content to: {output_path}")
            
        except PermissionError:
            raise PermissionError(
                f"Permission denied: Unable to write to {output_path}\n"
                "Please check file permissions."
            )
        except OSError as e:
            raise OSError(f"Error writing output file: {e}")
            
    except Exception as e:
        if "PDF" in str(type(e).__name__) or "pdf" in str(e).lower():
            raise Exception(f"Error reading PDF file: {e}")
        raise


def list_pdf_files() -> list[str]:
    """List all PDF files in the content folder."""
    content_folder = get_content_folder()
    
    if not content_folder.exists():
        return []
    
    return [f.name for f in content_folder.iterdir() if f.suffix.lower() == '.pdf']


def main():
    """Main entry point for the PDF reader."""
    print("=" * 50)
    print("PDF to Text Converter")
    print("=" * 50)
    
    # List available PDF files
    pdf_files = list_pdf_files()
    
    if not pdf_files:
        print("\nNo PDF files found in the content folder.")
        print(f"Please add a PDF file to: {get_content_folder()}")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s):")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf}")
    
    # If only one PDF, use it automatically
    if len(pdf_files) == 1:
        pdf_filename = pdf_files[0]
        print(f"\nProcessing: {pdf_filename}")
    else:
        # Let user choose
        try:
            choice = input("\nEnter the number of the PDF to process (or filename): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(pdf_files):
                    pdf_filename = pdf_files[index]
                else:
                    print("Invalid selection.")
                    return
            else:
                pdf_filename = choice
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
    
    # Process the PDF
    try:
        read_pdf_to_text(pdf_filename)
        print("\nDone! Check output.txt in the content folder.")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except PermissionError as e:
        print(f"\nPermission Error: {e}")
    except Exception as e:
        print(f"\nError processing PDF: {e}")


if __name__ == "__main__":
    main()
