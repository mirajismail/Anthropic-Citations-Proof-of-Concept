# PDF Document Analysis with Citations

Analyze multiple PDF documents simultaneously using AI with precise citations. Perfect for comparing financial reports, research papers, or any set of related documents.

## What This Application Does

- **Multi-document analysis**: Ask questions that span multiple PDF files
- **Smart document selection**: AI automatically picks the most relevant documents for your query
- **Concurrent processing**: Analyze multiple documents simultaneously for speed
- **Precise citations**: Every answer includes exact page references
- **Consolidated summaries**: Get both individual document responses and synthesized insights

## Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests python-dotenv
```

### 2. Configure API Access

Create a `.env` file:
```bash
SHOPIFY_API_TOKEN=your_shopify_api_token
SHOPIFY_API_URL=your_shopify_api_endpoint
```

### 3. Add Documents & Run

```bash
# Place PDF files in the project directory
# Then run the application
python3 citations_demo.py
```

## Example Usage

### Sample Session
```
Smart Citations Demo
Available documents:
  - Q1-2025-Press-Release-Final
  - Q2-2025-Press-Release-FINAL
  - Q3-2024-Press-Release-Final

Enter query (or 'exit'): What were the revenue trends across these quarters?

Selected 3 documents:
  - Q1-2025-Press-Release-Final
  - Q2-2025-Press-Release-FINAL  
  - Q3-2024-Press-Release-Final

Processing documents...
Made 3 API calls

================================================== Q1-2025-PRESS-RELEASE-FINAL.PDF ==================================================
Q1 2025 revenue reached $2.36 billion, representing 27% year-over-year growth...
  [Source: Q1-2025-Press-Release-Final.pdf, Pages: 1-1]

================================================== Q2-2025-PRESS-RELEASE-FINAL.PDF ==================================================
Q2 2025 revenue accelerated to $2.68 billion, showing 31% year-over-year growth...
  [Source: Q2-2025-Press-Release-FINAL.pdf, Pages: 1-1]

Summarizing...
============================================================
SUMMARY
============================================================
Revenue showed strong acceleration from Q3 2024 through Q2 2025, with growth rates 
improving from 26% to 31%. The trend shows consistent quarter-over-quarter improvement...
  [Source: Q1-2025-Press-Release-Final.pdf, Pages: 1-1]
  [Source: Q2-2025-Press-Release-FINAL.pdf, Pages: 1-1]
```

### Great Questions to Ask

**Comparative Analysis:**
- "Compare revenue growth across these quarters"
- "Which document shows the strongest performance improvements?"
- "How do key metrics trend over time?"

**Specific Extraction:**
- "What were the main challenges mentioned in Q1?"
- "Find all mentions of new product launches"
- "What guidance was provided for future quarters?"

**Synthesis Questions:**
- "What common themes appear across these reports?"
- "Which business factors consistently drive growth?"
- "How has the company's strategy evolved?"

## Key Features

### Intelligent Document Selection
The system uses AI to automatically select the most relevant documents for your question (up to 3 documents per query). No need to manually choose which PDFs to analyze.

### Accurate Citations
Every piece of information includes exact source and page references:
```
[Source: Document-Name.pdf, Pages: 2-4]
```

Use these to:
- Verify accuracy by checking source pages
- Understand which documents contribute which insights
- Build confidence in analysis results

### Two-Level Analysis
1. **Individual Responses** - See what each document says about your question
2. **Consolidated Summary** - Get synthesized insights combining information across documents

## Architecture

The application consists of two main components:

### SimpleDocumentSearch (`simple_search.py`)
- **Document Management**: SQLite database for PDF metadata
- **Smart Search**: AI-powered relevance scoring for document selection
- **Auto-Discovery**: Automatically finds and indexes PDF files

### Citations Demo (`citations_demo.py`)
- **Concurrent Processing**: ThreadPoolExecutor for parallel API calls
- **Citation Handling**: Preserves exact citation formatting from API responses
- **Result Synthesis**: Combines multiple document analyses into coherent summaries

## Tips for Best Results

### Writing Effective Questions
- **Be specific**: "What drove Q1 revenue growth?" vs "Tell me about performance"
- **Ask comparative questions**: "How do Q1 and Q2 compare?" works better than separate queries
- **Focus on insights**: "What explains the growth acceleration?" vs "What was the revenue?"

### Document Management
- Use descriptive filenames for better automatic selection
- Keep related documents in the same directory
- Ensure PDFs contain searchable text (not just scanned images)

## Troubleshooting

### Common Issues

**No Documents Found**
- Verify PDF files are in project root directory
- Check filenames don't contain special characters
- Ensure PDFs aren't password-protected

**API Errors**
- Verify `.env` credentials are correct
- Check API endpoint accessibility
- Confirm sufficient API quota

**Poor Document Selection**
- Use more specific questions
- Ensure document filenames are descriptive
- Consider which documents should actually be relevant

**Slow Performance**
- Application processes up to 3 documents concurrently
- Large PDFs take longer to process
- Network connectivity affects response times

## File Structure

```
Anthropic-Citations/
├── citations_demo.py          # Main application
├── simple_search.py           # Document search and management
├── simple_docs.db            # SQLite database (auto-created)
├── .env                      # API configuration
├── your-document.pdf         # Your PDF files
└── README.md                 # This file
```