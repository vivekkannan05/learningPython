# PDF to Text Converter

A simple Python project that reads PDF files and extracts their text content.

## Project Structure

```
learningPython/
├── content/          # Place your PDF files here
│   └── output.txt    # Generated text output
├── main.py           # Main Python script
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your PDF file(s) in the `content/` folder

2. Run the script:
   ```bash
   python main.py
   ```

3. The extracted text will be saved to `content/output.txt`

## Error Handling

The script handles the following error cases:

- **Missing content folder**: Creates an error message if the `content/` folder doesn't exist
- **Missing PDF file**: Notifies if no PDF files are found in the content folder
- **Output file issues**: Handles permission errors when writing the output file
- **Invalid PDF**: Catches errors when reading corrupted or invalid PDF files

## Example

```bash
$ python main.py
==================================================
PDF to Text Converter
==================================================

Found 1 PDF file(s):
  1. sample.pdf

Processing: sample.pdf
Reading PDF: /path/to/content/sample.pdf
Processing page 1/3...
Processing page 2/3...
Processing page 3/3...
Successfully wrote content to: /path/to/content/output.txt

Done! Check output.txt in the content folder.
```
