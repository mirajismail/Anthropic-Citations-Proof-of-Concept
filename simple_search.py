import sqlite3
import os
import re
import requests
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class SimpleDocumentSearch:
    def __init__(self, db_path: str = "simple_docs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create minimal table structure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_title TEXT NOT NULL,
                format TEXT NOT NULL,
                url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, file_title: str, format: str = "PDF", 
                    url: str = None, description: str = ""):
        """Add a document to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (file_title, format, url, description)
            VALUES (?, ?, ?, ?)
        ''', (file_title, format, url, description))
        
        conn.commit()
        conn.close()
    
    def search(self, query: str) -> List[Dict]:
        """Simple keyword search with basic filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Extract year and quarter from query
        year_match = re.search(r'20\d{2}', query)
        quarter_match = re.search(r'Q[1-4]|quarter\s*[1-4]', query, re.IGNORECASE)
        
        search_query = "SELECT * FROM documents WHERE 1=1"
        params = []
        
        # Filter by year if found
        if year_match:
            search_query += " AND fiscal_year = ?"
            params.append(year_match.group())
        
        # Filter by quarter if found
        if quarter_match:
            quarter = quarter_match.group().upper()
            if 'quarter' in quarter.lower():
                quarter = f"Q{re.search(r'[1-4]', quarter).group()}"
            search_query += " AND fiscal_quarter = ?"
            params.append(quarter)
        
        # Keyword search in title and keywords
        keywords = [w for w in query.lower().split() if w not in ['q1', 'q2', 'q3', 'q4', '2024', '2025']]
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append("(LOWER(title) LIKE ? OR LOWER(keywords) LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if keyword_conditions:
                search_query += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        search_query += " ORDER BY created_at DESC"
        
        cursor.execute(search_query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def llm_search(self, query: str) -> List[Dict]:
        """Use LLM to score document relevance to query."""
        docs = self.get_all_documents()
        if not docs:
            return []
        
        # Create scoring prompt
        doc_list = []
        for i, doc in enumerate(docs):
            doc_summary = f"{i+1}. {doc['file_title']} - {doc['description']}"
            doc_list.append(doc_summary)
        
        prompt = f"""User query: "{query}"

Available documents:
{chr(10).join(doc_list)}

Rate each document's relevance to the query on a scale of 0-10 (where 10 is most relevant).
Return only a JSON array of scores in order, like: [8, 3, 0, 9, 2]

Scores:"""
        
        try:
            payload = {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 100,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
            
            response = requests.post(
                os.getenv('SHOPIFY_API_URL'),
                json=payload,
                headers={"Authorization": f"Bearer {os.getenv('SHOPIFY_API_TOKEN')}"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                scores_text = response_data['content'][0]['text'].strip()
                
                # Parse JSON scores
                scores = json.loads(scores_text)
                
                # Combine docs with scores and sort
                scored_docs = list(zip(docs, scores))
                scored_docs.sort(key=lambda x: x[1], reverse=True)
                
                # Return docs with score > 0, sorted by relevance
                return [doc for doc, score in scored_docs if score > 0]
            
        except Exception as e:
            print(f"LLM search error: {e}")
            # Fallback to original search
            return self.search(query)
        
        return []
    
    def ingest_existing_pdfs(self):
        """Ingest PDF files from current directory."""
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            # Extract metadata from filename
            file_title = pdf_file.replace('.pdf', '')
            
            # Basic description - will be replaced with detailed ones
            description = f"Financial document: {file_title}"
            
            self.add_document(
                file_title=file_title,
                format="PDF",
                url=None,
                description=description
            )
            
            print(f"Added: {file_title}")

def main():
    """Test the search functionality."""
    search = SimpleDocumentSearch()
    
    # Ingest existing PDFs
    print("Ingesting PDF files...")
    search.ingest_existing_pdfs()
    
    print("\n" + "="*50)
    print("SEARCH TEST")
    print("="*50)
    
    # Test searches
    test_queries = [
        "revenue Q1 2025",
        "earnings Q2 2024", 
        "2025 results",
        "press release"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = search.search(query)
        
        if results:
            for doc in results:
                print(f"  ✓ {doc['title']} (Q{doc['fiscal_quarter']} {doc['fiscal_year']})")
        else:
            print("  No results found")
    
    # Interactive search
    print(f"\n{'='*50}")
    print("Interactive search (type 'exit' to quit):")
    while True:
        query = input("\nEnter search query: ").strip()
        if query.lower() == 'exit':
            break
            
        results = search.search(query)
        if results:
            for i, doc in enumerate(results, 1):
                print(f"{i}. {doc['title']}")
                print(f"   Year: {doc['fiscal_year']}, Quarter: {doc['fiscal_quarter']}")
                print(f"   Keywords: {doc['keywords']}")
        else:
            print("No results found")

if __name__ == "__main__":
    main()
    