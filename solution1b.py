import fitz
import json
import os
import time
import sys
from sentence_transformers import SentenceTransformer, util

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for i, b in enumerate(blocks):
            text_content = b[4].strip()
            if len(text_content.split()) > 10: # Only consider blocks with some substance
                text_blocks.append({
                    "doc": os.path.basename(pdf_path),
                    "page": page_num + 1,
                    "title": f"Page {page_num + 1}, Section {i+1}",
                    "content": text_content
                })
    return text_blocks

def run_analysis(request_path):
    with open(request_path) as f:
        request = json.load(f)

    docs = request["document_collection"]
    persona = request["persona"]
    job = request["job_to_be_done"]

    model = SentenceTransformer('/app/model') # Load model from within the container

    query = f"Persona: {persona}. Task: {job}"
    query_embedding = model.encode(query, convert_to_tensor=True)

    all_sections = []
    for doc_name in docs:
        full_path = os.path.join(os.path.dirname(request_path), doc_name)
        if os.path.exists(full_path):
            all_sections.extend(extract_text_from_pdf(full_path))

    if not all_sections: return {}

    section_contents = [sec["content"] for sec in all_sections]
    section_embeddings = model.encode(section_contents, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, section_embeddings)[0]

    for i, sec in enumerate(all_sections):
        sec['relevance_score'] = similarities[i].item()

    ranked_sections = sorted(all_sections, key=lambda x: x['relevance_score'], reverse=True)

    output = {
        "metadata": request,
        "extracted_sections": [{
            "document": s["doc"],
            "page_number": s["page"],
            "section_title": s["title"],
            "importance_rank": idx + 1,
            "refined_text": s["content"]
        } for idx, s in enumerate(ranked_sections[:10])]
    }
    return output

if __name__ == "__main__":
    request_file_path = sys.argv[1]
    result = run_analysis(request_file_path)

    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "challenge1b_output.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    print("Round 1B analysis complete.")