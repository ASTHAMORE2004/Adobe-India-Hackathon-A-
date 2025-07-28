import json
import os
import re
from typing import List, Dict, Any
import fitz  # PyMuPDF
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Heading:
    level: str
    text: str
    page: int
    font_size: float = 0.0
    font_flags: int = 0

class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = [
            # Chapter/Section patterns
            r'^(Chapter|Section|Part)\s+\d+[\.:]\s*(.+)',
            r'^(\d+\.?\d*\.?\d*)\s+(.+)',
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$',  # Title case headers
        ]
        
        # Keywords that often indicate headings
        self.heading_keywords = {
            'introduction', 'conclusion', 'abstract', 'summary', 'overview',
            'methodology', 'results', 'discussion', 'background', 'literature',
            'references', 'appendix', 'acknowledgments', 'contents', 'index'
        }
    
    def extract_title_from_document(self, doc: fitz.Document) -> str:
        """Extract document title from metadata or first page"""
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title'].strip()
        
        # Look for title on first page
        if len(doc) > 0:
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            # Find the largest text on first page as potential title
            largest_text = ""
            largest_size = 0
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["size"] > largest_size:
                                largest_size = span["size"]
                                largest_text = span["text"].strip()
            
            if largest_text and len(largest_text) > 3:
                return largest_text
        
        return "Untitled Document"
    
    def is_heading_candidate(self, text: str, font_size: float, font_flags: int, 
                           avg_font_size: float, common_font_size: float) -> bool:
        """Determine if text is likely a heading based on various criteria"""
        text_clean = text.strip()
        
        # Skip very short or very long text
        if len(text_clean) < 3 or len(text_clean) > 200:
            return False
        
        # Skip if it's just numbers or special characters
        if re.match(r'^[\d\s\.\-\(\)]+$', text_clean):
            return False
        
        # Check if text ends with common non-heading punctuation
        if text_clean.endswith(('.', '!', '?', ',', ';', ':')):
            return False
        
        # Font size criteria
        size_threshold = max(avg_font_size * 1.1, common_font_size * 1.05)
        if font_size >= size_threshold:
            return True
        
        # Bold or other formatting flags
        if font_flags & 2**4:  # Bold flag
            return True
        
        # Pattern matching
        for pattern in self.heading_patterns:
            if re.match(pattern, text_clean, re.IGNORECASE):
                return True
        
        # Keyword matching
        text_lower = text_clean.lower()
        if any(keyword in text_lower for keyword in self.heading_keywords):
            return True
        
        return False
    
    def determine_heading_level(self, heading: Heading, all_headings: List[Heading]) -> str:
        """Determine heading level based on font size and context"""
        font_sizes = [h.font_size for h in all_headings]
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Map font sizes to heading levels
        size_to_level = {}
        for i, size in enumerate(unique_sizes[:3]):  # Only H1, H2, H3
            size_to_level[size] = f"H{i+1}"
        
        return size_to_level.get(heading.font_size, "H3")
    
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Extract structured outline from PDF"""
        logger.info(f"Processing PDF: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        title = self.extract_title_from_document(doc)
        
        # Collect all text with formatting info
        all_text_info = []
        font_sizes = []
        
        for page_num in range(min(len(doc), 50)):  # Max 50 pages
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_font_size = 0
                        line_font_flags = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            line_font_size = max(line_font_size, span["size"])
                            line_font_flags |= span["flags"]
                        
                        if line_text.strip():
                            all_text_info.append({
                                'text': line_text.strip(),
                                'font_size': line_font_size,
                                'font_flags': line_font_flags,
                                'page': page_num + 1
                            })
                            font_sizes.append(line_font_size)
        
        # Calculate average and common font sizes
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
        common_font_size = max(set(font_sizes), key=font_sizes.count) if font_sizes else 12
        
        # Extract headings
        headings = []
        for info in all_text_info:
            if self.is_heading_candidate(
                info['text'], info['font_size'], info['font_flags'],
                avg_font_size, common_font_size
            ):
                headings.append(Heading(
                    level="",  # Will be determined later
                    text=info['text'],
                    page=info['page'],
                    font_size=info['font_size'],
                    font_flags=info['font_flags']
                ))
        
        # Determine heading levels
        for heading in headings:
            heading.level = self.determine_heading_level(heading, headings)
        
        # Sort by page number and remove duplicates
        seen = set()
        unique_headings = []
        for heading in sorted(headings, key=lambda h: (h.page, h.font_size)):
            if heading.text not in seen:
                seen.add(heading.text)
                unique_headings.append(heading)
        
        # Convert to required format
        outline = []
        for heading in unique_headings:
            outline.append({
                "level": heading.level,
                "text": heading.text,
                "page": heading.page
            })
        
        doc.close()
        
        return {
            "title": title,
            "outline": outline
        }

def main():
    """Main function to process PDFs from input directory"""
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDFs in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            
            try:
                # Extract outline
                result = extractor.extract_outline(pdf_path)
                
                # Save to output directory
                output_filename = filename.replace('.pdf', '.json')
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Processed {filename} -> {output_filename}")
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()