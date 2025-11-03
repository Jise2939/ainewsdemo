#!/usr/bin/env python3
"""
Check if full text can be extracted from article URLs
"""

import requests
from bs4 import BeautifulSoup

# Sample URLs from the test
test_urls = [
    "https://xapp.southcn.com/node_2ea31fe5fd/b150021036.shtml",
    "https://xapp.southcn.com/node_2ea31fe5fd/425846fd3b.shtml",
]

print("=" * 60)
print("CHECKING FULL TEXT AVAILABILITY FROM URLS")
print("=" * 60)

for i, url in enumerate(test_urls, 1):
    print(f"\n--- Testing URL {i} ---")
    print(f"URL: {url}")
    
    try:
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Try to parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for article content
        article_content = soup.find('article') or soup.find('div', class_='content') or soup.find('div', id='content')
        
        if article_content:
            text_content = article_content.get_text(strip=True)
            print(f"Found article content: {len(text_content)} characters")
            print(f"Preview: {text_content[:200]}...")
        else:
            # Get all text
            text = soup.get_text(strip=True)
            print(f"Total text length: {len(text)} characters")
            print(f"Preview: {text[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")

