# Applied AI Builder: Detailed Diagnostic Report (DDR) Generator

This system automatically converts Technical Inspection and Thermal Analysis PDF documents into a professional, structured Detailed Diagnostic Report (DDR).

## How it Works

1.  **Extraction**: Uses `pdfplumber` and `PyMuPDF` to extract text and images from uploaded PDFs.
2.  **Processing**: Merges findings from both reports, deduplicates observations, and detects conflicts or missing information.
3.  **AI Reasoning**: Uses Google Gemini (LLM) to analyze the data and generate a professional DDR in structured JSON format.
4.  **Reporting**: Converts the AI output into a client-ready HTML report and a downloadable PDF.

## Project Structure

```text
applied-ai-builder/
├── app.py              # Main Streamlit UI
├── requirements.txt    # Project dependencies
├── utils/
│   ├── __init__.py
│   ├── extraction.py   # PDF text and image extraction
│   ├── processor.py    # Data merging and merging logic
│   ├── ai_engine.py    # Gemini LLM integration
│   └── reporter.py     # HTML/PDF report generation
├── assets/             # Stored images and resources
└── temp_processing/    # Directory for active report processing
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 2. Installation
Clone the repository and install dependencies:
```bash
cd applied-ai-builder
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
```bash
streamlit run app.py
```

## Key Features
- **Accurate Data Merging**: Combines textual findings with thermal data.
- **Image Integration**: Extracts images and places them under relevant observations.
- **Severity Assessment**: AI-driven analysis of issue severity.
- **Missing Data Detection**: Explicitly lists information not provided in the input reports.
- **Dual Output**: Download reports in both HTML and PDF formats.

## License
MIT
