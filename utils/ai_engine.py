import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

def generate_ddr_json(prompt_input):
    """
    Calls the Gemini LLM to generate a structured DDR report in JSON format.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "Google API Key not found. Please set GOOGLE_API_KEY in .env file."}

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    system_instruction = """
    You are an Applied AI Report Builder. Your task is to generate a Detailed Diagnostic Report (DDR) from raw inspection and thermal data.
    
    RULES:
    1. DO NOT invent facts.
    2. If information is missing, write "Not Available".
    3. If sources conflict, explicitly mention the conflict.
    4. Use professional, non-technical language for a client-ready report.
    5. Output the result in a STRICT JSON format with the following keys:
       - property_issue_summary: (string)
       - area_wise_observations: (list of objects)
         - area: (string, e.g., Roof, Walls)
         - observation: (string)
         - thermal_findings: (string)
         - image_ids: (list of strings, use the provided IDs like "PAGE_X_IMG_Y" that match this observation context)
       - probable_root_cause: (string)
       - severity_assessment:
         - level: (Low/Medium/High)
         - reasoning: (string)
       - recommended_actions: (list of strings)
       - additional_notes: (string)
       - missing_information: (list of strings)
    
    MAPPING IMAGES:
    Use the provided 'IMAGE METADATA' (ID and Context) to decide which images belong to which observation. 
    Include the relevant image IDs in the 'image_ids' list for each area.
    """

    full_prompt = f"{system_instruction}\n\nINPUT DATA:\n{prompt_input}\n\nGenerate the JSON report now:"

    response = model.generate_content(full_prompt)
    
    try:
        # Extract JSON from response (handling potential markdown formatting)
        content = response.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    except Exception as e:
        return {"error": f"Failed to parse LLM response: {str(e)}", "raw_response": response.text}

def get_ddr_report(processed_data):
    """ Orchestrates the AI reasoning and returns the structured report. """
    from .processor import format_for_ai
    
    prompt_input = format_for_ai(processed_data)
    report_json = generate_ddr_json(prompt_input)
    
    return report_json
