"""
Utility functions for formatting data, citations, and reports.
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
import markdown
import os

class CitationFormatter:
    """Handles citation formatting for different styles."""
    
    @staticmethod
    def format_apa(author: str, title: str, source: str, year: str, url: str = "") -> str:
        """Format citation in APA style."""
        return f"{author}. ({year}). {title}. {source}. {url}"
    
    @staticmethod
    def format_mla(author: str, title: str, source: str, year: str, url: str = "") -> str:
        """Format citation in MLA style."""
        return f"{author}. \"{title}.\" {source}, {year}, {url}"
    
    @staticmethod
    def format_ieee(author: str, title: str, source: str, year: str, url: str = "") -> str:
        """Format citation in IEEE style."""
        return f"{author}, \"{title},\" {source}, {year}. [Online]. Available: {url}"

class ReportFormatter:
    """Handles report formatting and generation."""
    
    @staticmethod
    def format_markdown_report(
        title: str,
        introduction: str,
        literature_overview: str,
        summaries: List[Dict],
        comparison: Dict,
        key_takeaways: List[str],
        references: List[str],
        metadata: Dict
    ) -> str:
        """Format a complete research report in Markdown."""
        
        report = f"""# Research Report: {title}

## 🔍 Introduction
{introduction}

## 📖 Literature Overview
{literature_overview}

## 🧠 Summary of Key Sources

"""
        
        for i, summary in enumerate(summaries, 1):
            report += f"""### {i}. {summary.get('title', 'Untitled')}
**Source:** {summary.get('source', 'Unknown')}  
**Authors:** {summary.get('authors', 'Unknown')}  
**Published:** {summary.get('published', 'Unknown')}

**Summary:**
"""
            for bullet in summary.get('summary_bullets', []):
                report += f"- {bullet}\n"
            
            if summary.get('notable_quotes'):
                report += "\n**Notable Quotes:**\n"
                for quote in summary['notable_quotes']:
                    report += f"> {quote}\n"
            
            report += "\n---\n\n"
        
        report += f"""## ⚖️ Comparison of Viewpoints

### Agreements
"""
        for agreement in comparison.get('agreements', []):
            report += f"- {agreement}\n"
        
        report += "\n### Disagreements\n"
        for disagreement in comparison.get('disagreements', []):
            report += f"- {disagreement}\n"
        
        if comparison.get('noteworthy_biases'):
            report += "\n### Notable Biases\n"
            for bias in comparison['noteworthy_biases']:
                report += f"- {bias}\n"
        
        report += f"""

## ✅ Key Takeaways
"""
        for takeaway in key_takeaways:
            report += f"- {takeaway}\n"
        
        report += f"""

## 📚 References
"""
        for i, reference in enumerate(references, 1):
            report += f"{i}. {reference}\n"
        
        report += f"""

---
*Report generated on {metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}*
*Sources consulted: {metadata.get('sources_consulted', 'Unknown')}*
*Total articles analyzed: {metadata.get('articles_analyzed', 0)}*
"""
        
        return report
    
    @staticmethod
    def markdown_to_pdf(markdown_content: str, output_path: str) -> bool:
        """Convert markdown content to PDF."""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
            
            # Add CSS styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    h3 {{ color: #7f8c8d; }}
                    blockquote {{ border-left: 4px solid #3498db; padding-left: 20px; margin: 20px 0; }}
                    code {{ background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                    hr {{ border: none; border-top: 1px solid #ecf0f1; margin: 30px 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Use WeasyPrint to convert HTML to PDF
            from weasyprint import HTML
            HTML(string=styled_html).write_pdf(output_path)
            return True
            
        except Exception as e:
            print(f"Error converting to PDF: {e}")
            return False

class DataFormatter:
    """Handles data formatting and cleaning."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
        
        return text
    
    @staticmethod
    def extract_authors(author_string: str) -> List[str]:
        """Extract individual authors from a comma-separated string."""
        if not author_string:
            return []
        
        authors = [author.strip() for author in author_string.split(',')]
        return [author for author in authors if author]
    
    @staticmethod
    def format_date(date_string: str) -> str:
        """Format date string to standard format."""
        if not date_string:
            return "Unknown"
        
        try:
            # Try to parse common date formats
            date_formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%B %d, %Y",
                "%d %B %Y"
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_string, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If no format matches, return as is
            return date_string
            
        except Exception:
            return date_string
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """Truncate text to specified length while preserving word boundaries."""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + "..." 