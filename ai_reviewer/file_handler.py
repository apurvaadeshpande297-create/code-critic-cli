from pathlib import Path
from typing import Tuple, Optional

class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass

# Map extensions to programming languages for specialized prompts
SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".pyw": "Python",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".cppm": "C++",
    ".h": "C++",
    ".hpp": "C++",
    ".hxx": "C++",
}

def read_source_file(file_path_str: str) -> Tuple[str, str, Optional[str]]:
    """
    Validates and reads the contents of the given file path.
    
    Returns:
        A tuple of (file_content, detected_language, warning_message).
        If the language is not officially supported, returns 'Unknown' and a warning message.
    """
    path = Path(file_path_str)
    
    # 1. Existence and Type validation
    if not path.exists():
        raise FileHandlerError(f"The file path '{file_path_str}' does not exist.")
    if not path.is_file():
        raise FileHandlerError(f"The path '{file_path_str}' is a directory, not a source code file.")
        
    # 2. Extension detection
    ext = path.suffix.lower()
    language = SUPPORTED_EXTENSIONS.get(ext, "Unknown")
    
    warning_msg = None
    if language == "Unknown":
        warning_msg = (
            f"Warning: File extension '{ext}' is not officially supported (defaulting to .py and .cpp review models). "
            "AI will attempt a generic code review."
        )
        # Infer language from generic or fallback names
        language = "Generic"
        
    # 3. Read file contents
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            raise FileHandlerError(f"The file '{file_path_str}' is empty.")
        return content, language, warning_msg
    except Exception as e:
        raise FileHandlerError(f"Error reading file '{file_path_str}': {str(e)}")

def write_report_to_file(output_path_str: str, report_content: str) -> Path:
    """
    Saves the generated AI report to a markdown file.
    """
    path = Path(output_path_str)
    try:
        # Create directories if they do not exist
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report_content, encoding="utf-8")
        return path
    except Exception as e:
        raise FileHandlerError(f"Failed to write output report to '{output_path_str}': {str(e)}")
