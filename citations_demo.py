import requests
import base64
import os
import glob # this shouldn't be needed for actual app
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

# loads all docs in the dir
def load_documents():
    documents = {}
    for pdf_file in glob.glob("*.pdf"):
        with open(pdf_file, 'rb') as f:
            documents[pdf_file] = base64.b64encode(f.read()).decode('utf-8')
    return documents

# makes api request
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

# makes async requests using ThreadPoolExecutor
def concurrent_requests(documents, prompt):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, doc, content, prompt) for doc, content in documents.items()]
        return [f.result() for f in futures]

def print_results(results):
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

# Main execution
documents = load_documents()
print(f"Loaded {len(documents)} documents: {list(documents.keys())}")

while True:
    prompt = input("\nEnter your prompt (or 'exit'): ")
    if prompt.lower() == 'exit':
        break
    if prompt.strip():
        results = concurrent_requests(documents, prompt)
        print_results(results)