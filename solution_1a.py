import fitz  # This is PyMuPDF
import json
import os
import time
import numpy as np

# This part figures out which font sizes are for headings
def get_font_statistics(doc):
    font_counts = {}
    # Go through every page to count font sizes
    for page in doc:
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    font_counts[s['size']] = font_counts.get(s['size'], 0) + 1

    if not font_counts: return {}, None

    # Find the most common font size (that's your normal text)
    body_size = max(font_counts, key=font_counts.get)

    # Headings are bigger than normal text
    heading_sizes = sorted([size for size in font_counts if size > body_size + 0.5], reverse=True)

    # Assign H1, H2, H3 to the biggest sizes
    size_map = {}
    if len(heading_sizes) > 0: size_map[heading_sizes[0]] = "H1"
    if len(heading_sizes) > 1: size_map[heading_sizes[1]] = "H2"
    if len(heading_sizes) > 2: size_map[heading_sizes[2]] = "H3"

    # The title is usually the biggest text on the first page
    title_size = 0
    first_page_blocks = doc[0].get_text("dict", flags=11)["blocks"]
    for b in first_page_blocks:
        for l in b["lines"]:
            for s in l["spans"]:
                if s['size'] > title_size: title_size = s['size']

    return size_map, title_size

# This part pulls out the text using the font info
def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    if doc.page_count == 0: return {"title": "", "outline": []}

    size_map, title_size = get_font_statistics(doc)
    outline = []
    doc_title = ""
    title_found = False

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if not text: continue

                    # Find title on first page
                    if not title_found and page_num == 0 and s['size'] == title_size:
                        doc_title = text
                        title_found = True
                        continue

                    # Find headings
                    if s['size'] in size_map:
                        if len(text.split()) < 20: # Make sure it's not a long paragraph
                            outline.append({"level": size_map[s['size']], "text": text, "page": page_num + 1})

    return {"title": doc_title, "outline": outline}

# This is the main part that runs everything
if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)

            output_filename = f"{os.path.splitext(filename)[0]}.json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w") as f:
                json.dump(result, f, indent=4)
            print(f"Processed {filename}, created {output_filename}")