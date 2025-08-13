# Shopify Citations API Demo

Concurrent API calls to analyze multiple PDF documents with citations.

## Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install requests python-dotenv
   ```

3. **Configure environment**
   Create `.env` file:
   ```
   SHOPIFY_API_TOKEN=your_token_here
   SHOPIFY_API_URL=your_api_url_here
   ```

4. **Add PDF documents**
   Place PDF files in the project directory

## Usage

```bash
python3 citations_demo.py
```

**Example flow:**
```
Loaded 3 documents: ['Q1-2025-Press-Release-Final.pdf', 'Q2-2025-Press-Release-FINAL.pdf', 'Q3-2024-Press-Release-Final.pdf']

Enter your prompt (or 'exit'): Compare the revenue growth trajectories across these quarters and identify which business factors are driving the strongest performance improvements.

Made 3 API calls

================================================== Q1-2025-PRESS-RELEASE-FINAL.PDF ==================================================
Revenue grew 27% year-over-year to $2.36 billion, driven by merchant solutions growth...
  [Source: Q1-2025-Press-Release-Final.pdf, Pages: 1-2]

================================================== Q2-2025-PRESS-RELEASE-FINAL.PDF ==================================================
Revenue accelerated to 31% growth reaching $2.68 billion, with strong GMV expansion...
  [Source: Q2-2025-Press-Release-FINAL.pdf, Pages: 1-1]

================================================== Q3-2024-PRESS-RELEASE-FINAL.PDF ==================================================
Revenue growth of 26% to $2.16 billion, with improved free cash flow margins...
  [Source: Q3-2024-Press-Release-Final.pdf, Pages: 1-1]
```

## Features

- Loads all PDFs automatically
- Makes concurrent API calls (max 5 workers in this case)
- Returns responses with document citations
- Logs API call count