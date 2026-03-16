import fitz  # PyMuPDF
import os
import io
from PIL import Image

def extract_content(pdf_path, output_image_dir):
    """
    Extracts text and images from a PDF.
    Returns a list of dictionaries, one for each page, containing text and image metadata.
    """
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)

    content = []
    
    # Use PyMuPDF for both text and image extraction as it provides better positional info
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        page_data = {
            "page_number": page_num + 1,
            "text": page.get_text("text") or "",
            "images": []
        }
        
        # Extract images and their surrounding text context
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"page_{page_num+1}_img_{img_index}.{image_ext}"
            image_path = os.path.join(output_image_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            # Capture context: Get blocks of text on the same page
            # We'll take text blocks near the image if possible, or just the page text
            # For simplicity and reliability in mapping, we'll store the page number and a unique ID
            image_id = f"PAGE_{page_num+1}_IMG_{img_index}"
            
            # Simple heuristic: text within 200 character proximity in the raw text stream
            # or just provide the whole page text to the LLM to decide.
            # We'll provide a 'context' snippet here.
            page_text = page_data["text"]
            
            page_data["images"].append({
                "path": image_path,
                "id": image_id,
                "context": page_text[:1000] # Provide some context for the LLM to map
            })
        
        content.append(page_data)
    
    doc.close()
    return content

def extract_all_documents(inspection_pdf, thermal_pdf, base_assets_dir):
    """
    Extracts content from both reports and returns a merged structure.
    """
    inspection_assets = os.path.join(base_assets_dir, "inspection")
    thermal_assets = os.path.join(base_assets_dir, "thermal")
    
    inspection_data = extract_content(inspection_pdf, inspection_assets)
    thermal_data = extract_content(thermal_pdf, thermal_assets)
    
    return {
        "inspection": inspection_data,
        "thermal": thermal_data
    }
