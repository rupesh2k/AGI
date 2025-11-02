"""
Example usage of the Check Extraction Agent
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.check_extraction_agent import CheckExtractionAgent


def example_basic_extraction():
    """Example of basic check extraction without LLM."""
    print("=" * 50)
    print("Example 1: Basic Check Extraction (Regex-based)")
    print("=" * 50)
    
    agent = CheckExtractionAgent(use_llm=False)
    
    # Replace with actual check file path
    check_file = "path/to/your/check.jpg"
    
    try:
        # Extract check information
        writer_name, check_number = agent.extract_check_info(check_file)
        
        print(f"Writer Name: {writer_name}")
        print(f"Check Number: {check_number}")
        
        # Rename the file
        new_path = agent.rename_check_file(check_file)
        print(f"File renamed to: {new_path}")
        
    except FileNotFoundError:
        print(f"File not found: {check_file}")
        print("Please update the check_file path with an actual check image.")
    except Exception as e:
        print(f"Error: {e}")


def example_llm_extraction():
    """Example of LLM-enhanced check extraction."""
    print("\n" + "=" * 50)
    print("Example 2: LLM-Enhanced Check Extraction")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY not found in environment.")
        print("Please set it in .env file for LLM mode.")
        return
    
    agent = CheckExtractionAgent(use_llm=True, openai_api_key=openai_api_key)
    
    # Replace with actual check file path
    check_file = "path/to/your/check.jpg"
    
    try:
        # Extract check information
        writer_name, check_number = agent.extract_check_info(check_file)
        
        print(f"Writer Name: {writer_name}")
        print(f"Check Number: {check_number}")
        
        # Rename the file
        new_path = agent.rename_check_file(check_file, output_dir="./processed")
        print(f"File renamed to: {new_path}")
        
    except FileNotFoundError:
        print(f"File not found: {check_file}")
        print("Please update the check_file path with an actual check image.")
    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing():
    """Example of processing multiple check files."""
    print("\n" + "=" * 50)
    print("Example 3: Batch Processing Multiple Checks")
    print("=" * 50)
    
    agent = CheckExtractionAgent(use_llm=False)
    
    # Directory containing check files
    checks_dir = Path("path/to/checks")
    
    if not checks_dir.exists():
        print(f"Directory not found: {checks_dir}")
        print("Please update the checks_dir path with actual checks directory.")
        return
    
    # Process all image and PDF files
    image_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    check_files = [
        f for f in checks_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ]
    
    print(f"Found {len(check_files)} check file(s) to process")
    
    for check_file in check_files:
        try:
            print(f"\nProcessing: {check_file.name}")
            new_path = agent.rename_check_file(
                str(check_file),
                output_dir="./processed"
            )
            print(f"✓ Renamed to: {Path(new_path).name}")
        except Exception as e:
            print(f"✗ Error processing {check_file.name}: {e}")


if __name__ == "__main__":
    example_basic_extraction()
    # example_llm_extraction()  # Uncomment if you have OpenAI API key
    # example_batch_processing()  # Uncomment to process multiple files

