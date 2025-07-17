import requests
import base64
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_API_URL = os.getenv('SHOPIFY_API_URL')

def validate_document(file_path):
    """Validate document against API limits."""
    try:
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Check file size (32MB limit)
        if file_size > 32 * 1024 * 1024:
            print(f"Error: File size {file_size_mb:.1f}MB exceeds 32MB limit")
            return False
        
        # Use PyPDF2 to read the number of pages
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            num_pages = len(reader.pages)
        
        if num_pages > 100:
            print(f"Error: Document has {num_pages} pages, exceeds 100-page limit")
            return False
        
        print(f"Document validation passed: {file_size_mb:.1f}MB, {num_pages} pages")
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return False
    except Exception as e:
        print(f"Error validating document: {str(e)}")
        return False

def readable_response(response):
    print("=" * 80)
    print("BATCH QUERY RESPONSES")
    print("=" * 80)
    
    for item in response['content']:
        text = item.get('text', '')
        print(text)
        
        # Check for any citations associated with this text
        citations = item.get('citations', [])
        for citation in citations:
            # Format citation details nicely
            doc_title = citation.get('document_title', 'Unknown Document')
            start_page = citation.get('start_page_number', 'NA')
            end_page = citation.get('end_page_number', 'NA')
            print(f"  [Cited from: {doc_title}, Pages: {start_page}-{end_page}]")
    
    print("\n" + "=" * 80)

    # Token usage summary
    usage = response.get('usage', {})
    input_tokens = usage.get('input_tokens', 'NA')
    output_tokens = usage.get('output_tokens', 'NA')
    print("TOKEN USAGE SUMMARY:")
    print(f"  Input Tokens: {input_tokens}")
    print(f"  Output Tokens: {output_tokens}")
    print("=" * 80)

# pdf_file_path = 'Shopify Annual Financial Report 2024.pdf'
pdf_file_path = 'Pattern Recognition and Machine Learning Chapter 2.pdf'
if not validate_document(pdf_file_path):
    print("Exiting due to document validation failure.")
    exit(1)

# Load PDF as base64 for document upload
with open(pdf_file_path, 'rb') as pdf_file:
    pdf_content_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')


while True:
    # Collect multiple questions from user
    questions = []
    print("Enter your questions about the document (type 'done' when finished, 'exit' to quit):")
    while True:
        question = input(f"Question {len(questions) + 1}: ")
        if question.lower() == 'done':
            break
        if question.lower() == 'exit':
            exit()
        if question.strip():  # Only add non-empty questions
            questions.append(question.strip())

    # Format questions into a single prompt
    if questions:
        query_text = "Please answer the following questions about the document:\n\n" + \
                     "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    else:
        continue

    # payload for the request
    payload = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_content_base64
                        },
                        "title": "Pattern Recognition and Machine Learning Chapter 2",
                        "context": "Academic textbook chapter on pattern recognition and machine learning.",
                        "citations": {"enabled": True}
                    },
                    {
                        "type": "text",
                        "text": query_text
                    }
                ]
            }
        ]
    }

    # Set headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SHOPIFY_API_TOKEN}"
    }

    # Make the request
    response = requests.post(SHOPIFY_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        readable_response(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

