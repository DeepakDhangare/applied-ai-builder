import re

def clean_text(text):
    """Basic text cleaning."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_extracted_data(extracted_data):
    """
    Processes extracted data from both reports.
    Identifies areas, deduplicates, and prepares a structured prompt-ready format.
    """
    inspection_raw = extracted_data.get("inspection", [])
    thermal_raw = extracted_data.get("thermal", [])
    
    # Combine text by source for global context
    inspection_text = "\n".join([f"PAGE {p['page_number']}: {clean_text(p['text'])}" for p in inspection_raw])
    thermal_text = "\n".join([f"PAGE {p['page_number']}: {clean_text(p['text'])}" for p in thermal_raw])
    
    # Collect all images with metadata
    all_images = []
    for page in inspection_raw:
        for img_obj in page["images"]:
            all_images.append({
                "path": img_obj["path"],
                "id": img_obj["id"],
                "source": "inspection",
                "page": page["page_number"],
                "context": clean_text(img_obj["context"])
            })
    
    for page in thermal_raw:
        for img_obj in page["images"]:
            all_images.append({
                "path": img_obj["path"],
                "id": img_obj["id"],
                "source": "thermal",
                "page": page["page_number"],
                "context": clean_text(img_obj["context"])
            })
            
    processed_data = {
        "inspection_raw": inspection_text,
        "thermal_raw": thermal_text,
        "images": all_images,
        "merging_notes": []
    }
    
    if not inspection_text.strip():
        processed_data["merging_notes"].append("Warning: Inspection report text is missing or unextractable.")
    if not thermal_text.strip():
        processed_data["merging_notes"].append("Warning: Thermal report text is missing or unextractable.")
        
    return processed_data

def format_for_ai(processed_data):
    """
    Formats the processed data into a structured string for the AI prompt.
    """
    image_metadata = "\n".join([
        f"- ID: {img['id']} (from {img['source']} p.{img['page']}). Context: {img['context'][:200]}..."
        for img in processed_data['images']
    ])

    prompt_input = f"""
### INSPECTION REPORT CONTENT ###
{processed_data['inspection_raw']}

### THERMAL REPORT CONTENT ###
{processed_data['thermal_raw']}

### IMAGE METADATA (Use IDs to map images to observations) ###
{image_metadata if image_metadata else "No images extracted."}
    """
    
    if processed_data['merging_notes']:
        prompt_input += "\n### PROCESSING NOTES ###\n" + "\n".join(processed_data['merging_notes'])
        
    return prompt_input
