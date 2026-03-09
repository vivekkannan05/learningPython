"""
Tree Folder PDF Reader - Project 2
Traverses sub-folders under /content, finds all PDF files,
extracts their text, and writes output.txt in each sub-folder.
"""

import os
from pathlib import Path
from PyPDF2 import PdfReader

def get_content_folder() -> Path:
    """Get the content folder path."""
    return Path(__file__).parent / "content"

def find_subfolders(content_folder: Path) -> list[Path]:
    """Return a list of sub-folder paths inside the content folder."""
    if not content_folder.exists():
        raise FileNotFoundError(
            f"Content folder does not exist: {content_folder}\n"
            "Please create the 'content' folder with sub-folders."
        )

    subfolders = [f for f in content_folder.iterdir() if f.is_dir()]
    if not subfolders:
        print("No sub-folders found under content/.")
    return sorted(subfolders)

def find_pdf_files(folder: Path) -> list[Path]:
    """Return all PDF files in the given folder."""
    return sorted(folder.glob("*.pdf"))

def extract_pdf_text(pdf_path: Path) -> str:
    """Extract and return all text from a PDF file."""
    reader = PdfReader(pdf_path)
    text_parts = []
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(f"--- Page {i} ---\n{page_text}\n")
        else:
            text_parts.append(f"--- Page {i} ---\n[No extractable text]\n")

    return "\n".join(text_parts)

def write_output(folder: Path, text: str) -> None:
    """Write the extracted text to a file in the given folder."""
    output_path = folder / "output.txt"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Successfully wrote content to: {output_path}")
    except PermissionError:
        raise PermissionError(
            f"Permission denied: Unable to write to {output_path}\n"
            "Please check file permissions."
        )
    except OSError as e:
        raise OSError(f"Error writing output file: {e}")

def process_folder(folder: Path) -> None:
    """Process all PDF files in the given folder and write their text to output.txt."""
    print(f"\n Processing folder: {folder.name}")

    pdf_files = find_pdf_files(folder)
    if not pdf_files:
        print(f"No PDF files found in {folder.name}")
        return

    all_text = []
    for pdf in pdf_files:
        try:
            text = extract_pdf_text(pdf)
            all_text.append(f"--- File: {pdf.name} ---\n{text}\n")
        except Exception as e:
            print(f"Error processing PDF {pdf}: {e}")
            continue

    if all_text:
        combined_text = "\n".join(all_text)
        write_output(folder, combined_text)
    else:
        print(f"No text extracted from PDF files in {folder.name}")

def main() -> None:
    """Main entry point for the PDF reader."""
    print("=" * 50)
    print("Tree Folder PDF Reader")
    print("=" * 50)

    content_folder = get_content_folder()
    subfolders = find_subfolders(content_folder)
    if not subfolders:
        print("No sub-folders found under content/.")
        return
    
    print(f"\nFound {len(subfolders)} sub-folders:")
    for i, folder in enumerate(subfolders, 1):
        print(f"  {i}. {folder.name}")

    for folder in subfolders:
        process_folder(folder)

    print("\nAll processing complete!")
    print("Text extracted from PDF files has been written to output.txt in each sub-folder.")
    print("=" * 50)

if __name__ == "__main__":
    main()