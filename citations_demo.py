import requests
import base64
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from simple_search import SimpleDocumentSearch

load_dotenv()

def make_request(doc_name, doc_content, prompt):
    payload = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {"type": "base64", "media_type": "application/pdf", "data": doc_content},
                    "title": doc_name,
                    "citations": {"enabled": True}
                },
                {"type": "text", "text": prompt}
            ]
        }]
    }
    
    response = requests.post(
        os.getenv('SHOPIFY_API_URL'),
        json=payload,
        headers={"Authorization": f"Bearer {os.getenv('SHOPIFY_API_TOKEN')}"}
    )
    
    return {"doc": doc_name, "data": response.json() if response.status_code == 200 else None}

def print_results(results):
    """Print raw citations API results."""
    print(f"\nMade {len(results)} API calls")
    for result in results:
        print(f"\n{'='*50} {result['doc'].upper()} {'='*50}")
        if result['data']:
            for item in result['data']['content']:
                print(item.get('text', ''))
                for citation in item.get('citations', []):
                    print(f"  [Source: {citation.get('document_title', 'Unknown')}, Pages: {citation.get('start_page_number', 'N/A')}-{citation.get('end_page_number', 'N/A')}]")
        else:
            print("Error in response")

def summarize_with_citations(prompt, results):
    """Summarize results while preserving exact citations from the API."""
    
    # Collect all responses with citations
    responses_with_citations = []
    
    for result in results:
        if result['data']:
            for item in result['data']['content']:
                text = item.get('text', '')
                citations = item.get('citations', [])
                
                if text.strip():
                    response_block = f"From {result['doc']}:\n{text}"
                    
                    # Add citations exactly as returned by API
                    for citation in citations:
                        source = citation.get('document_title', 'Unknown')
                        start_page = citation.get('start_page_number', 'N/A')
                        end_page = citation.get('end_page_number', 'N/A')
                        response_block += f"\n[Source: {source}, Pages: {start_page}-{end_page}]"
                    
                    responses_with_citations.append(response_block)
    
    if not responses_with_citations:
        return None
    
    # Create summarization prompt
    all_responses = "\n\n".join(responses_with_citations)
    
    summarization_prompt = f"""User asked: "{prompt}"

Here are the responses from the documents with their citations:

{all_responses}

Please provide a consolidated summary that answers the user's question. 
IMPORTANT: Keep all the citation information exactly as provided above - do not modify the [Source: X, Pages: Y-Z] format.
When you reference information, include the citation that came with it.

Summary:"""

    try:
        payload = {
            "model": "claude-3-7-sonnet-20250219",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": summarization_prompt}]
        }
        
        response = requests.post(
            os.getenv('SHOPIFY_API_URL'),
            json=payload,
            headers={"Authorization": f"Bearer {os.getenv('SHOPIFY_API_TOKEN')}"}
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
    except Exception as e:
        print(f"Summarization error: {e}")
    
    return None

def main():
    search = SimpleDocumentSearch()
    
    print("Smart Citations Demo")
    print("Available documents:")
    for doc in search.get_all_documents():
        print(f"  - {doc['file_title']}")
    
    while True:
        prompt = input("\nEnter query (or 'exit'): ")
        if prompt.lower() == 'exit':
            break
            
        # Select relevant documents
        results = search.llm_search(prompt)[:3]
        if not results:
            print("No relevant documents found")
            continue
            
        print(f"Selected {len(results)} documents:")
        for doc in results:
            print(f"  - {doc['file_title']}")
        
        # Load and process documents
        documents = {}
        for doc in results:
            file_path = doc['file_title'] + '.pdf'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    documents[file_path] = base64.b64encode(f.read()).decode('utf-8')
        
        # Run citations API
        print("Processing documents...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, doc, content, prompt) 
                      for doc, content in documents.items()]
            api_results = [f.result() for f in futures]
        
        # Show raw API results
        print_results(api_results)
        
        # Summarize with preserved citations
        print("\nSummarizing...")
        summary = summarize_with_citations(prompt, api_results)
        
        if summary:
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            print(summary)
        else:
            print("Summarization failed")

if __name__ == "__main__":
    main()
