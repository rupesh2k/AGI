"""
Main script for running utility agents
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agents.check_extraction_agent import CheckExtractionAgent

# Load environment variables
load_dotenv()


def extract_and_rename_check(file_path: str, use_llm: bool = False, output_dir: str = None):
    """
    Extract check information and rename the file.
    
    Args:
        file_path: Path to the check file (image or PDF)
        use_llm: Whether to use LLM for better extraction (requires OPENAI_API_KEY)
        output_dir: Optional directory to save renamed file
    """
    # Get OpenAI API key if using LLM
    openai_api_key = os.getenv("OPENAI_API_KEY") if use_llm else None
    
    if use_llm and not openai_api_key:
        print("Warning: LLM mode requested but OPENAI_API_KEY not found in environment.")
        print("Falling back to regex-based extraction.")
        use_llm = False
    
    # Initialize agent
    agent = CheckExtractionAgent(use_llm=use_llm, openai_api_key=openai_api_key)
    
    try:
        print(f"Processing check file: {file_path}")
        print("Extracting check information...")
        
        # Extract info first (before renaming)
        writer_name, check_number = agent.extract_check_info(file_path)
        
        if not writer_name or not check_number:
            raise ValueError(
                f"Could not extract check information. "
                f"Writer name: {writer_name}, Check number: {check_number}"
            )
        
        # Rename the file
        new_path = agent.rename_check_file(file_path, output_dir)
        
        print(f"✓ Successfully renamed to: {new_path}")
        print(f"  Writer Name: {writer_name}")
        print(f"  Check Number: {check_number}")
        
        return new_path
        
    except Exception as e:
        print(f"Error processing check: {str(e)}", file=sys.stderr)
        return None


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <check_file_path> [--llm] [--output-dir <dir>]")
        print("\nOptions:")
        print("  --llm              Use LLM for better extraction (requires OPENAI_API_KEY)")
        print("  --output-dir DIR   Save renamed file to specified directory")
        print("\nExample:")
        print("  python main.py check.jpg")
        print("  python main.py check.jpg --llm")
        print("  python main.py check.jpg --output-dir ./processed")
        sys.exit(1)
    
    file_path = sys.argv[1]
    use_llm = "--llm" in sys.argv
    output_dir = None
    
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    extract_and_rename_check(file_path, use_llm, output_dir)


if __name__ == "__main__":
    main()

