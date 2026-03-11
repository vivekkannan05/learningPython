"""
PDF Question Extractor
Reads a PDF file, extracts questions using regex patterns, and stores them in MySQL.
"""

from pathlib import Path
from PyPDF2 import PdfReader
import argparse
import json
import re
import mysql.connector
from mysql.connector import Error as MySQLError

def load_database_config() -> dict:
    confg_path = Path(__file__).parent / "config.json"
    if not confg_path.exists():
        raise FileNotFoundError(f"Database config file not found: {confg_path}")
    with open(confg_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    db_config = config.get("database", {})
    required_keys = ["host", "port", "user", "password", "database"]
    missing = [key for key in required_keys if key not in db_config]
    if missing:
        raise ValueError(f"Missing required database configuration keys: {', '.join(missing)}")
    return db_config

def connect_to_database(db_config: dict):
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print(f"Connected to database: {db_config['database']}")
            return conn
        else:
            raise MySQLError("Failed to connect to database. Connection not established.")
    except MySQLError as e:
        raise MySQLError(f"Failed to connect to database: {e}")

def close_database_connection(conn: mysql.connector.connection.MySQLConnection):
    if conn.is_connected():
        conn.close()
def load_regex_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Regex config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    question_regex = config.get("question_regex", "")
    chapter_regex = config.get("chapter_regex", "")

    if not question_regex:
        raise ValueError("question_regex is not configured in config.json")
    if not chapter_regex:
        raise ValueError("chapter_regex is not configured in config.json")

    for name, pattern in [("question_regex", question_regex), ("chapter_regex", chapter_regex)]:
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid {name} in config.json: {e}")

    return {"question_regex": question_regex, "chapter_regex": chapter_regex}


def ensure_table_exists(conn: mysql.connector.connection.MySQLConnection, table_name: str):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_name VARCHAR(255),
        chapter_name VARCHAR(255),
        question_text TEXT,
        answer_options TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table '{table_name}' is ready.")
    except MySQLError as e:
        raise MySQLError(f"Failed to create table '{table_name}': {e}")
    finally:
        if cursor is not None:
            cursor.close()

def insert_data_into_database(conn: mysql.connector.connection.MySQLConnection, table_name: str, data: tuple) -> None:
    insert_query = f"""
    INSERT INTO {table_name} (subject_name, chapter_name, question_text, answer_options, answer)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(insert_query, data)
        conn.commit()
    except MySQLError as e:
        conn.rollback()
        raise MySQLError(f"Failed to insert data into table '{table_name}': {e}")
    finally:
        if cursor is not None:
            cursor.close()

def get_content_folder() -> Path:
    """Get the content folder path."""
    return Path(__file__).parent / "content"


def read_pdf_and_store(pdf_filename: str, page_number: int, regex_config: dict) -> None:
    """
    Read a PDF file, extract questions using regex, and store them in the database.

    Args:
        pdf_filename: Name of the PDF file to read (e.g., "document.pdf")
        page_number: The page number to extract from
        regex_config: Dict with 'question_regex' and 'chapter_regex' patterns
    """
    content_folder = get_content_folder()
    pdf_path = content_folder / pdf_filename

    if not content_folder.exists():
        raise FileNotFoundError(
            f"Content folder does not exist: {content_folder}\n"
            "Please create the 'content' folder in the project directory."
        )

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}\n"
            "Please place a PDF file in the 'content' folder."
        )

    if not pdf_filename.lower().endswith('.pdf'):
        raise ValueError(f"File '{pdf_filename}' is not a PDF file.")

    try:
        print(f"Reading PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        if page_number > total_pages or page_number < 1:
            raise ValueError(f"Invalid page number: {page_number}. Must be between 1 and {total_pages}.")

        page = reader.pages[page_number - 1]
        page_text = page.extract_text()
        if not page_text:
            print("[No extractable text on this page]")
            return

        subject_name = Path(pdf_filename).stem.replace(" Questions", "").replace(" questions", "")

        chapter_match = re.search(regex_config["chapter_regex"], page_text)
        chapter_name = chapter_match.group(1).strip() if chapter_match else f"Page {page_number}"

        questions = list(re.finditer(regex_config["question_regex"], page_text))
        if not questions:
            print(f"No questions found on page {page_number}.")
            return

        print(f"Found {len(questions)} question(s) on page {page_number}.")

        conn = None
        try:
            db_config = load_database_config()
            conn = connect_to_database(db_config)
            ensure_table_exists(conn, "questions")

            for match in questions:
                question_text = match.group(1).strip()
                answer_options = "\t".join([
                    match.group(2).strip(),
                    match.group(3).strip(),
                    match.group(4).strip(),
                    match.group(5).strip()
                ])
                answer = match.group(6).strip()
                print(f"  Inserting: {question_text[:50]}...")

                data = (subject_name, chapter_name, question_text, answer_options, answer)
                insert_data_into_database(conn, "questions", data)

            print(f"Successfully inserted {len(questions)} question(s) into database.")
        except (MySQLError, ConnectionError, ValueError) as e:
            print(f"Database error (PDF was read successfully): {e}")
        finally:
            if conn:
                close_database_connection(conn)

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

def parse_args() :
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Extract text from a specific page of a PDF file.")
    parser.add_argument("page_number", type=int, help="The page number to extract text from.")
    return parser.parse_args()


def main():
    """Main entry point for the PDF reader."""
    print("=" * 50)
    print("PDF Question Extractor (Regex + DB)")
    print("=" * 50)

    args = parse_args()
    page_number = args.page_number
    try:
        regex_config = load_regex_config()
    except (ValueError, FileNotFoundError) as e:
        print(f"\nConfig error: {e}")
        return

    pdf_files = list_pdf_files()

    if not pdf_files:
        print("\nNo PDF files found in the content folder.")
        print(f"Please add a PDF file to: {get_content_folder()}")
        return

    print(f"\nFound {len(pdf_files)} PDF file(s):")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf}")

    if len(pdf_files) == 1:
        pdf_filename = pdf_files[0]
        print(f"\nProcessing: {pdf_filename}")
    else:
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

    try:
        read_pdf_and_store(pdf_filename, page_number, regex_config)
        print("\nDone!")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nError processing PDF: {e}")


if __name__ == "__main__":
    main()
