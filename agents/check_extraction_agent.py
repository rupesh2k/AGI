"""
Check Extraction Utility Agent
Extracts check information (writer name and check number) and renames files accordingly.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.tools import tool
except ImportError:
    # Fallback if LangChain is not available
    pass


class CheckExtractionAgent:
    """
    Agent that extracts check information from images or PDFs and renames files.
    """
    
    def __init__(self, use_llm: bool = False, openai_api_key: Optional[str] = None):
        """
        Initialize the Check Extraction Agent.
        
        Args:
            use_llm: Whether to use LLM for better extraction (requires OpenAI API key)
            openai_api_key: OpenAI API key if using LLM mode
        """
        self.use_llm = use_llm
        self.llm = None
        self.agent_executor = None
        
        if use_llm and openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=openai_api_key
            )
            self._setup_agent()
    
    def _setup_agent(self):
        """Setup LangChain agent with tools."""
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain.tools import tool
        
        @tool
        def extract_text_from_image(image_path: str) -> str:
            """Extract text from an image file using OCR."""
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        
        @tool
        def parse_check_info(text: str) -> dict:
            """Parse check information from extracted text. Returns writer name and check number."""
            # This will be enhanced by the LLM
            return {"writer_name": "", "check_number": ""}
        
        tools = [extract_text_from_image, parse_check_info]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a check extraction agent. Your task is to:
1. Extract text from check images using OCR
2. Identify the check writer's name (usually in "Pay to the order of" field)
3. Identify the check number (usually in the top right corner)
4. Return the information in a structured format.

Be precise and accurate in extracting this information."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from image or PDF file using OCR.
        
        Args:
            file_path: Path to the check file (image or PDF)
            
        Returns:
            Extracted text from the file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle PDF files
        if file_path.suffix.lower() == '.pdf':
            images = convert_from_path(str(file_path))
            if not images:
                raise ValueError("Could not extract images from PDF")
            # Use first page for now
            image = images[0]
        else:
            # Handle image files
            image = Image.open(file_path)
        
        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        return text
    
    def extract_check_info(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract check writer name and check number from a file.
        
        Args:
            file_path: Path to the check file
            
        Returns:
            Tuple of (writer_name, check_number) or (None, None) if not found
        """
        text = self.extract_text_from_file(file_path)
        
        if self.use_llm and self.agent_executor:
            # Use LLM for better extraction
            result = self.agent_executor.invoke({
                "input": f"Extract the check writer name and check number from this text:\n\n{text}"
            })
            # Parse LLM response to extract structured data
            # This would need custom parsing based on LLM response format
            writer_name = self._parse_writer_name_llm(result)
            check_number = self._parse_check_number_llm(result)
        else:
            # Use regex-based extraction
            writer_name = self._parse_writer_name(text)
            check_number = self._parse_check_number(text)
        
        return writer_name, check_number
    
    def _parse_writer_name(self, text: str) -> Optional[str]:
        """Parse check writer name from extracted text using regex."""
        # Common patterns for "Pay to the order of" field
        patterns = [
            r'Pay\s+to\s+the\s+order\s+of[:\s]+([A-Za-z\s]+)',
            r'PAY\s+TO\s+THE\s+ORDER\s+OF[:\s]+([A-Za-z\s]+)',
            r'Payable\s+to[:\s]+([A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean up common OCR errors
                name = re.sub(r'\s+', ' ', name)
                return name.title()
        
        return None
    
    def _parse_check_number(self, text: str) -> Optional[str]:
        """Parse check number from extracted text using regex."""
        # Check number patterns - usually 3-6 digits, often near "No." or "Check #"
        patterns = [
            r'No\.?\s*[:\s]*(\d{3,6})',
            r'Check\s*#?\s*[:\s]*(\d{3,6})',
            r'#?\s*(\d{3,6})\s*$',  # At end of line
            r'Check\s+Number[:\s]+(\d{3,6})',
        ]
        
        # Look for patterns
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Take the first reasonable match
                for match in matches:
                    if len(match) >= 3:  # At least 3 digits
                        return match
        
        # Fallback: look for isolated 3-6 digit numbers (might be check number)
        isolated_numbers = re.findall(r'\b\d{3,6}\b', text)
        if isolated_numbers:
            # Filter out common non-check numbers (dates, amounts, etc.)
            # Check numbers are typically 4-6 digits
            for num in isolated_numbers:
                if 4 <= len(num) <= 6:
                    return num
        
        return None
    
    def _parse_writer_name_llm(self, result: dict) -> Optional[str]:
        """Parse writer name from LLM result."""
        # Implement based on LLM response format
        # This is a placeholder - would need to parse actual LLM response
        return None
    
    def _parse_check_number_llm(self, result: dict) -> Optional[str]:
        """Parse check number from LLM result."""
        # Implement based on LLM response format
        # This is a placeholder - would need to parse actual LLM response
        return None
    
    def rename_check_file(self, file_path: str, output_dir: Optional[str] = None) -> str:
        """
        Extract check info and rename the file as: writer_name_check_number.ext
        
        Args:
            file_path: Path to the check file
            output_dir: Optional directory to save renamed file (default: same directory)
            
        Returns:
            Path to the renamed file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract check information
        writer_name, check_number = self.extract_check_info(str(file_path))
        
        if not writer_name or not check_number:
            raise ValueError(
                f"Could not extract check information. "
                f"Writer name: {writer_name}, Check number: {check_number}"
            )
        
        # Sanitize writer name for filename (remove invalid characters)
        safe_writer_name = re.sub(r'[^\w\s-]', '', writer_name)
        safe_writer_name = re.sub(r'\s+', '_', safe_writer_name)
        safe_writer_name = safe_writer_name.strip('_')
        
        # Create new filename
        extension = file_path.suffix
        new_filename = f"{safe_writer_name}_{check_number}{extension}"
        
        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / new_filename
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_path = file_path.parent / new_filename
        
        # Rename/move file
        file_path.rename(output_path)
        
        return str(output_path)

