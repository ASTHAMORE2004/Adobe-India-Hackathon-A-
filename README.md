# Adobe-India-Hackathon-A-
PDF Outline Extractor - Round 1A
PDF Outline Extractor - Round 1A
Overview
This solution extracts structured outlines from PDF documents, identifying titles and hierarchical headings (H1, H2, H3) with their corresponding page numbers.
Approach
1. Title Extraction

Metadata First: Attempts to extract title from PDF metadata
First Page Analysis: If metadata is unavailable, identifies the largest text on the first page as the potential title
Fallback: Uses "Untitled Document" if no suitable title is found

2. Heading Detection
The solution uses multiple criteria to identify headings:
Font-based Analysis

Size Threshold: Text with font size 1.1x average or 1.05x most common size
Bold Formatting: Text with bold formatting flags
Relative Sizing: Compares font sizes across the document

Pattern Recognition

Chapter/Section patterns: "Chapter 1:", "Section 2.1"
Numbered patterns: "1.1", "2.3.1"
All-caps headers: "INTRODUCTION", "METHODOLOGY"
Title case headers: "Literature Review", "Data Analysis"

Keyword-based Detection

Academic keywords: introduction, methodology, results, discussion, conclusion
Document structure keywords: abstract, summary, references, appendix

3. Heading Level Determination

Font Size Hierarchy: Larger font sizes → higher hierarchy (H1 > H2 > H3)
Unique Size Mapping: Maps the 3 largest unique font sizes to H1, H2, H3
Context Awareness: Considers the document's overall structure

4. Quality Assurance

Duplicate Removal: Eliminates duplicate headings based on text content
Length Filtering: Removes very short (<3 chars) or very long (>200 chars) text
Pattern Validation: Excludes text that's just numbers or special characters
Punctuation Check: Filters out text ending with sentence-ending punctuation

Libraries Used

PyMuPDF (fitz): PDF processing and text extraction with formatting information
dataclasses: Type-safe data structures
re: Regular expression pattern matching
json: Output formatting
logging: Process monitoring

Model Information

No ML Models: This solution uses rule-based algorithms only
Model Size: 0MB (no trained models)
Dependencies: Lightweight libraries totaling <50MB

Build and Run Instructions
Build Docker Image

''' docker build --platform linux/amd64 -t pdf-outline-extractor:v1.0 .'''

run container 
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:v1.0

Input/Output Structure

Input: Place PDF files in the input/ directory
Output: JSON files generated in output/ directory with same filename but .json extension


EXAMPLE FORMAT:
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}

Performance Characteristics

Speed: Processes 50-page PDFs in under 10 seconds
Memory: Efficient memory usage with streaming processing
Accuracy: High precision through multi-criteria heading detection
Scalability: Handles multiple PDFs in batch processing

Multilingual Support

Unicode Support: Handles various character encodings
Language Agnostic: Pattern recognition works across languages
Bonus Feature: Special handling for Japanese and other non-Latin scripts

Error Handling

Graceful Degradation: Continues processing even if individual PDFs fail
Logging: Comprehensive error logging and progress tracking
Validation: Input validation and format checking

Limitations

Works best with well-formatted PDFs with clear visual hierarchy
May struggle with heavily formatted documents or scanned PDFs
Performance depends on document complexity and structure
