# JSON Annotation Extractor (built for Readera backup file library.json)

This script, `extract_annotations.py`, is designed to parse a JSON file containing book data and extract specific annotation details. It can output the extracted information to the console or generate separate, formatted PDF files for each book's annotations.

## Extracted Information

For each annotation found, the script extracts:
- Book Name (`doc_title` or `doc_file_name_title` from the JSON)
- Page Number (`note_page` from the JSON)
- Quote (`note_body` from the JSON - the text that was annotated)
- Annotation (`note_extra` from the JSON - the user's note/comment)

## JSON Format Expectation

The script expects the input JSON to have a top-level key `docs`, which is an array of document objects. Each document object that contains annotations should have:
- A `data` object, which in turn has a `doc_title` (or `doc_file_name_title`).
- A `citations` array, where each item represents an annotation and contains `note_page`, `note_body`, and `note_extra`.

A `sample_data.json` file is provided in this repository to illustrate the expected format (including multiple books) and to allow for testing of the script.

## Dependencies

This script requires the `reportlab` library for PDF generation. Install it and other potential dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## How to Use

1.  **Ensure you have Python installed.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the script from your terminal.** You need to provide the path to your JSON file.

    **To print annotations to the console:**
    ```bash
    python extract_annotations.py /path/to/your/data.json
    ```
    For example, using the sample data:
    ```bash
    python extract_annotations.py sample_data.json
    ```

    **To generate PDF files for annotations:**
    Use the `--pdf` flag. This will generate a separate PDF file for each book found in the input JSON.
    ```bash
    python extract_annotations.py /path/to/your/data.json --pdf
    ```
    For example:
    ```bash
    python extract_annotations.py sample_data.json --pdf
    ```
    This will create PDF files in the current directory, named like `[Book_Title]_Annotations.pdf` (e.g., `All_American_Boys_Annotations.pdf`, `The_Great_Gatsby_Annotations.pdf`).

## PDF Output Format

When using the `--pdf` flag:
- A separate PDF document is created for each book that has annotations.
- The filename of each PDF will be `[Book_Title]_Annotations.pdf` (spaces in the title are replaced with underscores, and other problematic characters are removed).
- Inside each PDF:
    - The **Book Title** is displayed as a bold, centered heading at the top.
    - Annotations are presented in a **table** with three columns:
        - **Page No.** (centered)
        - **Quote** (left-aligned, text will wrap)
        - **Annotation** (left-aligned, text will wrap)
    - The table includes a header row, grid lines, and alternating background colors for readability.

## Example Console Output (without `--pdf` flag, using `sample_data.json`)

```
Extracted Annotations (Console Output):
  Book: All American Boys
  Page: 4
  Quote: "STONES"
  Annotation: "Cool"
--------------------
  Book: All American Boys
  Page: 20
  Quote: "Important point about Rashad."
  Annotation: "This really highlights his perspective."
--------------------
  Book: The Great Gatsby
  Page: 35
  Quote: "Green light"
  Annotation: "Symbolism of hope and dreams."
--------------------
  Book: The Great Gatsby
  Page: 60
  Quote: "Eyes of Dr. T. J. Eckleburg"
  Annotation: "Watching over the characters, like the eyes of God."
--------------------
```

## Example PDF Generation Confirmation (with `--pdf` flag)
When running with `--pdf`, you will see messages like:
```
Successfully generated PDF: All_American_Boys_Annotations.pdf
Successfully generated PDF: The_Great_Gatsby_Annotations.pdf
```

## Error Handling
- The script handles file not found, JSON decoding errors, and unexpected JSON structures.
- If `reportlab` encounters an issue during PDF generation, an error message will be printed for the specific book's PDF.
- If no annotations are found, appropriate messages are displayed.
```
