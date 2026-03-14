import streamlit as st
import os
import shutil
from utils.extraction import extract_all_documents
from utils.processor import process_extracted_data
from utils.ai_engine import get_ddr_report
from utils.reporter import save_report, generate_html
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Applied AI Builder - DDR Generator", layout="wide")

st.title("🏗️ Applied AI Builder: DDR Generator")
st.markdown("""
Convert raw Inspection and Thermal PDF reports into structured, client-ready Detailed Diagnostic Reports (DDR).
""")

# Setup sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password").strip()
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    st.info("Ensure you have a valid Gemini API Key.")

# File upload section
col1, col2 = st.columns(2)
with col1:
    inspection_file = st.file_uploader("Upload Inspection Report (PDF)", type=["pdf"])
with col2:
    thermal_file = st.file_uploader("Upload Thermal Report (PDF)", type=["pdf"])

if st.button("Generate DDR Report", disabled=not (inspection_file and thermal_file)):
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("Please provide a Google API Key in the sidebar.")
    else:
        with st.status("🚀 Processing documents...", expanded=True) as status:
            # Create temp directories
            temp_dir = "temp_processing"
            assets_dir = os.path.join(temp_dir, "assets")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(assets_dir)
            
            # Save uploaded files temporarily
            inspection_path = os.path.join(temp_dir, "inspection.pdf")
            thermal_path = os.path.join(temp_dir, "thermal.pdf")
            
            with open(inspection_path, "wb") as f:
                f.write(inspection_file.getbuffer())
            with open(thermal_path, "wb") as f:
                f.write(thermal_file.getbuffer())
                
            st.write("🔍 Extracting text and images...")
            extracted_data = extract_all_documents(inspection_path, thermal_path, assets_dir)
            
            st.write("🧠 Analyzing data and detecting conflicts...")
            processed_data = process_extracted_data(extracted_data)
            
            st.write("🤖 Generating AI Insights (Gemini)...")
            report_json = get_ddr_report(processed_data)
            
            if "error" in report_json:
                st.error(report_json["error"])
                status.update(label="❌ Generation failed", state="error")
            else:
                st.write("📄 Formatting Final DDR Report...")
                
                # Create a lookup for image paths by ID
                image_lookup = {img["id"]: img["path"] for img in processed_data["images"]}
                
                # Map extracted images to report based on AI-provided IDs
                for area in report_json.get("area_wise_observations", []):
                    area["image_paths"] = []
                    for img_id in area.get("image_ids", []):
                        if img_id in image_lookup:
                            area["image_paths"].append(os.path.abspath(image_lookup[img_id]))

                html_path, pdf_path = save_report(report_json, temp_dir)
                
                status.update(label="✅ Report generated successfully!", state="complete")
                
                st.success("DDR Report is ready!")
                
                # Report Preview
                st.header("Report Preview")
                html_content = generate_html(report_json)
                st.components.v1.html(html_content, height=800, scrolling=True)
                
                # Download buttons
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download PDF Report", f, file_name="DDR_Report.pdf", mime="application/pdf")
                with col_d2:
                    with open(html_path, "r") as f:
                        st.download_button("Download HTML Report", f.read(), file_name="DDR_Report.html", mime="text/html")

elif not (inspection_file and thermal_file):
    st.info("Please upload both reports to start.")
