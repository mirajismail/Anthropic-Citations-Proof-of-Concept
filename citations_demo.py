import requests
import base64
import os

# Constants
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the tokens and URLs from environment variables
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_API_URL = os.getenv('SHOPIFY_API_URL')

def readable_response(response):
    print("=" * 80)
    print("BATCH QUERY RESPONSES")
    print("=" * 80)
    
    for item in response['content']:
        text = item.get('text', '')
        # Output the text components directly
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
    # Print tokens usage for insight
    usage = response.get('usage', {})
    input_tokens = usage.get('input_tokens', 'NA')
    output_tokens = usage.get('output_tokens', 'NA')
    print("TOKEN USAGE SUMMARY:")
    print(f"  Input Tokens: {input_tokens}")
    print(f"  Output Tokens: {output_tokens}")
    print("=" * 80)

# Load PDF as base64 for document upload
# Replace with the actual path to your Shopify financial report
with open('Pattern Recognition and Machine Learning Chapter 2.pdf', 'rb') as pdf_file:
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

    # Define the payload for the request
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

    # Make the POST request
    response = requests.post(SHOPIFY_API_URL, json=payload, headers=headers)

    # Check the response
    if response.status_code == 200:
        readable_response(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

