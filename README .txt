# Persona-Driven Document Intelligence - Round 1B

## Overview
This solution builds an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done.

## Approach

### 1. Document Structure Analysis
- **PDF Text Extraction**: Uses PyMuPDF to extract text with formatting information
- **Section Identification**: Identifies document sections based on:
  - Font size variations
  - Heading patterns (Chapter, Section, numbered headings)
  - Academic keywords (Introduction, Methodology, Results, etc.)
  - Visual formatting cues (bold, size differences)

### 2. Persona-Driven Relevance Scoring
The system calculates relevance scores using a multi-factor approach:

#### Persona Classification
- **Researcher**: Focuses on methodology, results, analysis, experiments
- **Student**: Emphasizes definitions, concepts, examples, theories
- **Analyst**: Targets trends, revenue, metrics, performance data
- **Journalist**: Looks for facts, events, sources, timeline information
- **Entrepreneur**: Seeks opportunities, strategies, market insights

#### Job-to-be-Done Mapping
- **Literature Review**: Methodology, previous work, gaps, comparisons
- **Exam Preparation**: Key concepts, definitions, formulas, examples
- **Financial Analysis**: Revenue, expenses, performance metrics, trends
- **Market Research**: Market size, competitors, opportunities, segments

### 3. Relevance Scoring Algorithm
```
Relevance Score = (Persona Score × 0.4) + (Job Score × 0.6) + Importance Boost

Where:
- Persona Score: Keyword density for persona-specific terms
- Job Score: Keyword density for job-specific terms
- Importance Boost: Bonus for critical terms (key, important, essential)
```

### 4. Section Ranking and Selection
- **Relevance-Based Ranking**: Sections ranked by calculated relevance scores
- **Importance Ranking**: Assigns numerical ranks (1 = most important)
- **Top-N Selection**: Selects most relevant sections for output
- **Page-Level Tracking**: Maintains page number references for easy navigation

### 5. Subsection Analysis
- **Content Segmentation**: Breaks sections into meaningful subsections
- **Paragraph-Level Analysis**: Analyzes individual paragraphs for relevance
- **Length Optimization**: Ensures subsections are substantial (>50 characters)
- **Refinement**: Provides concise, relevant text excerpts

## Libraries Used
- **PyMuPDF (fitz)**: PDF processing and text extraction
- **NumPy**: Numerical operations for scoring calculations
- **dataclasses**: Type-safe data structures
- **re**: Regular expression pattern matching
- **json**: Input/output formatting
- **datetime**: Timestamp generation
- **logging**: Process monitoring

## Model Information
- **No ML Models**: Rule-based algorithm with keyword matching
- **Model Size**: 0MB (no trained models)
- **Dependencies**: Lightweight libraries totaling <100MB

## Build and Run Instructions

### Build Docker Image
```bash
docker build --platform linux/amd64 -t persona-doc-intelligence:v1.0 .
```

### Run Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none persona-doc-intelligence:v1.0
```

### Input Structure
Place in `input/` directory:
- Multiple PDF files (3-10 documents)
- `config.json` file with persona and job definition:

```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

### Output Structure
Generates `challenge1b_output.json` with:
- **Metadata**: Input documents, persona, job, timestamp
- **Extracted Sections**: Ranked sections with importance scores
- **Subsection Analysis**: Refined text excerpts with relevance scores

## Performance Characteristics
- **Processing Time**: <60 seconds for 3-5 documents
- **Memory Efficient**: Processes documents sequentially
- **Scalable**: Handles various document types and sizes
- **Generic**: Works across different domains and personas

## Supported Use Cases

### Academic Research
- Literature reviews from research papers
- Methodology extraction and comparison
- Results and findings analysis

### Business Analysis
- Financial report analysis
- Market research compilation
- Competitive intelligence gathering

### Educational Content
- Study material organization
- Key concept extraction
- Exam preparation assistance

### Journalism
- Fact gathering from multiple sources
- Timeline construction
- Background research compilation

## Error Handling
- **Graceful Degradation**: Continues processing despite individual document failures
- **Input Validation**: Validates persona and job definitions
- **Comprehensive Logging**: Detailed process tracking and error reporting
- **Fallback Mechanisms**: Default handling for edge cases

## Limitations
- Performance depends on document quality and structure
- Keyword-based approach may miss semantic relationships
- Limited to CPU processing (no GPU acceleration)
- Best suited for well-formatted, text-rich documents

## Future Enhancements
- Semantic similarity using lightweight embedding models
- Dynamic keyword expansion based on context
- Multi-language support optimization
- Advanced section boundary detection