from datetime import datetime
from typing import Dict, Optional
import os

class ResultFormatterModule:
    def __init__(self):
        self.md_template = """# Audio Summary Report

## Overview
Generated on: {timestamp}

## Summary
{summary}

---
*This summary was automatically generated from audio content.*
"""
    def _format_markdown(self, summary: str) -> str:
        """Format the summary into a well-structured markdown document."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the summary with some basic markdown enhancements
        formatted_summary = summary.replace('\n\n', '\n\n> ')  # Add blockquotes for paragraphs
        if not formatted_summary.startswith('> '):
            formatted_summary = '> ' + formatted_summary

        return self.md_template.format(
            timestamp=timestamp,
            summary=formatted_summary,
        )

    def _format_text(self, summary: str) -> str:
        """Format the summary into a clean text document."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""Audio Summary Report
Generated on: {timestamp}

{summary}

---
This summary was automatically generated from audio content."""

    def format_results(self, summary: str, output_dir: str, task_id: str) -> Dict[str, str]:
        """
        Format the summary into both .md and .txt files and return their paths.
        
        Args:
            summary: The summary text to format
            output_dir: Directory to save the formatted files
            task_id: Unique identifier for the task
            additional_notes: Optional additional notes to include in the markdown version
            
        Returns:
            Dictionary containing paths to the generated files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate file paths
        md_path = os.path.join(output_dir, f"{task_id}_summary.md")
        txt_path = os.path.join(output_dir, f"{task_id}_summary.txt")
        
        # Format and save markdown
        md_content = self._format_markdown(summary)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        # Format and save text
        txt_content = self._format_text(summary)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
            
        return {
            "md": md_path,
            "txt": txt_path
        }

# Initialize the formatter module
result_formatter = ResultFormatterModule() 