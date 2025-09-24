#!/usr/bin/env python3
"""
Study Analyzer Web Server - Save as server.py
Run: python server.py
Then open: http://localhost:8000
"""

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
import os

# Azure OpenAI Configuration - UPDATE THIS!
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = "gpt-35-turbo"
API_VERSION = "2025-01-01-preview"

SYSTEM_PROMPT = """You are an expert research methodology analyst. Return a JSON response with this structure:
{
  "qualityScore": number (1-10),
  "sampleSize": "description with assessment",
  "sampleSizeScore": number (1-10),
  "pValueInterpretation": "p-value found and interpretation",
  "pValueScore": number (1-10),
  "effectSize": "effect size description",
  "effectSizeScore": number (1-10),
  "studyDesign": "study type and quality",
  "designScore": number (1-10),
  "warnings": ["list of concerns"],
  "recommendations": ["what to look for next"],
  "summary": "2-3 sentence plain English summary"
}

Focus on statistical vs practical significance, sample sizes, p-hacking, effect sizes, and study design quality."""

def analyze_study(study_text):
    url = f"{AZURE_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    
    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_KEY
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this study:\n\n{study_text}"}
        ],
        "max_tokens": 1500,
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    return json.loads(result['choices'][0]['message']['content'])

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"index.html not found! Make sure it's in the same folder.")
    
    def do_POST(self):
        if self.path == '/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                study_text = data.get('studyText', '').strip()
                if not study_text:
                    raise Exception("No study text provided")
                
                analysis = analyze_study(study_text)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(analysis).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == "__main__":
    print("Starting Study Analyzer Server...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Looking for index.html...")
    
    if not os.path.exists('index.html'):
        print("ERROR: index.html not found in this folder!")
        print("Files in current directory:")
        for file in os.listdir('.'):
            print(f"   - {file}")
        print("\nPlease save the HTML file as 'index.html' next to this server.py")
        input("Press Enter to exit...")
        exit()
    else:
        print("Found index.html!")
    
    if AZURE_KEY == "your-actual-api-key-here":
        print("Please update AZURE_KEY with your real API key!")
        print("Edit server.py and replace 'your-actual-api-key-here' with your key")
        input("Press Enter to continue anyway...")
    else:
        print("API key configured!")
    
    print("Starting HTTP server on port 8000...")
    
    try:
        server = HTTPServer(('', 8000), Handler)
        print("Server started successfully!")
        print("Open your browser to: http://localhost:8000")
        print("Press Ctrl+C to stop")
        print("Waiting for requests...")
        server.serve_forever()
    except OSError as e:
        print(f"Failed to start server: {e}")
        print("Try a different port or check if another program is using port 8000")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        input("Press Enter to exit...")