import json
import sys
import argparse
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def extract_annotations_from_json(filepath):
    """
    Extracts book annotations from a JSON file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
              'book_name', 'page_number', 'quote', and 'annotation'.
              Returns an empty list if the file cannot be processed or
              no annotations are found.
    """
    extracted_data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return []

    if 'docs' not in data or not isinstance(data['docs'], list):
        print("Error: JSON structure is not as expected. Missing 'docs' array.")
        return []

    for doc in data['docs']:
        book_name = doc.get('data', {}).get('doc_title')
        if not book_name:
            # Try an alternative if doc_title is missing or empty
            book_name = doc.get('data', {}).get('doc_file_name_title', 'Unknown Title')


        citations = doc.get('citations')
        if not citations or not isinstance(citations, list):
            continue

        for citation in citations:
            page_number = citation.get('note_page')
            quote = citation.get('note_body')
            # Based on the provided JSON, 'note_extra' seems to be the annotation.
            annotation = citation.get('note_extra')

            if quote and annotation: # Ensure essential fields are present
                extracted_data.append({
                    'book_name': book_name,
                    'page_number': page_number,
                    'quote': quote,
                    'annotation': annotation
                })

    return extracted_data

def sanitize_filename(filename):
    """Removes or replaces characters that are problematic in filenames."""
    # Remove characters that are definitely not allowed or problematic
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # You might want to add more rules, e.g., for leading/trailing dots, reserved names, etc.
    # Truncate if too long (many file systems have a limit around 255 characters)
    return filename[:200]

def save_book_to_pdf(book_title, book_annotations, base_path="."):
    """
    Saves annotations for a single book to a PDF file.

    Args:
        book_title (str): The title of the book.
        book_annotations (list): A list of annotation dicts for this book.
        base_path (str): The directory where the PDF will be saved.
    """
    if not book_annotations:
        print(f"No annotations to save for {book_title}.")
        return

    safe_title = sanitize_filename(book_title)
    pdf_filename = os.path.join(base_path, f"{safe_title}_Annotations.pdf")

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    # Book Title
    title_style = styles['h1']
    title_style.alignment = 1 # Center alignment
    title_text = Paragraph(book_title, title_style)
    story.append(title_text)
    story.append(Spacer(1, 0.25 * inch))

    # Table Data
    # Header row
    data = [["Page No.", "Quote", "Annotation"]]

    # Annotation rows
    for ann in book_annotations:
        # Ensure all parts are strings for Paragraph
        page_str = str(ann.get('page_number', 'N/A'))
        quote_str = str(ann.get('quote', ''))
        annotation_str = str(ann.get('annotation', ''))

        # Create Paragraph objects for text wrapping in cells
        page_p = Paragraph(page_str, styles['Normal'])
        quote_p = Paragraph(quote_str, styles['Normal'])
        annotation_p = Paragraph(annotation_str, styles['Normal'])
        data.append([page_p, quote_p, annotation_p])

    if len(data) == 1: # Only header, no annotations
        story.append(Paragraph("No annotations found for this book.", styles['Normal']))
    else:
        # Create Table
        table = Table(data, colWidths=[0.75*inch, 3*inch, 3*inch]) # Adjust column widths as needed

        # Table Style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey), # Header row background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), # Align all cells left
            ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Align first column (Page No.) center
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12), # Header bottom padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige), # Data rows background (alternating would be more complex)
            ('GRID', (0, 0), (-1, -1), 1, colors.black), # Grid lines
            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Top align content in cells
        ])
        table.setStyle(style)
        story.append(table)

    try:
        doc.build(story)
        print(f"Successfully generated PDF: {pdf_filename}")
    except Exception as e:
        print(f"Error generating PDF for {book_title}: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extracts book annotations from a JSON file and optionally generates PDFs.")
    parser.add_argument("json_filepath", help="Path to the input JSON file.")
    parser.add_argument("--pdf", action="store_true", help="Generate a separate PDF for each book's annotations.")

    args = parser.parse_args()

    all_annotations_data = extract_annotations_from_json(args.json_filepath)

    if not all_annotations_data:
        print("No annotations found or an error occurred while reading the JSON.")
        sys.exit(0)

    if args.pdf:
        # Group annotations by book_name
        books_data = {}
        for item in all_annotations_data:
            book_name = item['book_name']
            if book_name not in books_data:
                books_data[book_name] = []
            # We only need page, quote, annotation for the PDF table, book_name is the key
            books_data[book_name].append({
                'page_number': item['page_number'],
                'quote': item['quote'],
                'annotation': item['annotation']
            })

        if not books_data:
            print("No books found to generate PDFs for.")
        else:
            for book_title, annotations_for_book in books_data.items():
                save_book_to_pdf(book_title, annotations_for_book)
    else:
        # Print to console (original behavior)
        print("\nExtracted Annotations (Console Output):")
        for item in all_annotations_data:
            print(f"  Book: {item['book_name']}")
            print(f"  Page: {item['page_number']}")
            print(f"  Quote: \"{item['quote']}\"")
            print(f"  Annotation: \"{item['annotation']}\"")
            print("-" * 20)
