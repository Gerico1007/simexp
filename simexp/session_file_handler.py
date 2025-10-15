"""
SimExp Session File Handler
Handles file operations for session management

♠️🌿🎸🧵 G.Music Assembly - File Integration Feature
"""

import os
from pathlib import Path
from typing import Optional
import mimetypes

class SessionFileHandler:
    """Handles file operations for session content"""
    
    # Mapping of file extensions to language identifiers for code blocks
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.md': 'markdown',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sh': 'bash',
        '.bash': 'bash',
        '.txt': 'text'
    }

    @staticmethod
    def read_file(file_path: str) -> str:
        """
        Read file content and return as string
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            str: File content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def detect_language(file_path: str) -> str:
        """
        Detect programming language based on file extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Language identifier for markdown code block
        """
        ext = Path(file_path).suffix.lower()
        return SessionFileHandler.LANGUAGE_MAP.get(ext, 'text')

    @staticmethod
    def format_content(file_path: str, content: str, heading: Optional[str] = None) -> str:
        """
        Format file content for Simplenote with appropriate markdown
        
        Args:
            file_path: Path to the file (for language detection)
            content: Raw file content
            heading: Optional heading to add before content
            
        Returns:
            str: Formatted content ready for Simplenote
        """
        formatted = []
        
        # Add heading if provided
        if heading:
            formatted.append(f"## {heading}")
            formatted.append("")
        
        # Add file info
        formatted.append(f"**File:** `{os.path.basename(file_path)}`")
        formatted.append("")
        
        # Format content based on file type
        language = SessionFileHandler.detect_language(file_path)
        if language != 'markdown':  # Don't wrap markdown in code blocks
            formatted.append(f"```{language}")
            formatted.append(content)
            formatted.append("```")
        else:
            formatted.append(content)
            
        return "\n".join(formatted)