# AGI - Agentic Framework Utilities

A collection of utility agents built with an agentic framework for automating various tasks.

## Overview

This project implements utility agents using LangChain and other agentic frameworks to automate repetitive tasks. Each agent is designed to handle specific utility functions.

## Utility Agents

### 1. Check Extraction Agent

Extracts check information (writer name and check number) from check images or PDFs and automatically renames files.

**Features:**
- Extracts text from check images using OCR (Tesseract)
- Supports both image formats (PNG, JPG) and PDF files
- Identifies check writer name (from "Pay to the order of" field)
- Identifies check number
- Automatically renames files as: `writer_name_check_number.ext`
- Optional LLM-enhanced extraction for better accuracy

**Usage:**

```bash
# Basic usage (regex-based extraction)
python main.py check.jpg

# Use LLM for better extraction (requires OPENAI_API_KEY)
python main.py check.jpg --llm

# Specify output directory
python main.py check.jpg --output-dir ./processed
```

**Python API:**

```python
from agents.check_extraction_agent import CheckExtractionAgent

# Initialize agent
agent = CheckExtractionAgent(use_llm=False)

# Extract and rename
new_path = agent.rename_check_file("check.jpg")

# Or extract info manually
writer_name, check_number = agent.extract_check_info("check.jpg")
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

3. (Optional) For LLM-enhanced extraction, set up OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Requirements

- Python 3.8+
- Tesseract OCR
- (Optional) OpenAI API key for LLM mode

## Project Structure

```
AGI/
├── agents/
│   ├── __init__.py
│   └── check_extraction_agent.py  # Check extraction utility agent
├── main.py                         # Main script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore
└── README.md
```

## Contributing

More utility agents will be added in the future. Each agent follows a similar pattern:
- Located in `agents/` directory
- Implements a specific utility function
- Can be used both as a library and via command line

## License

MIT

