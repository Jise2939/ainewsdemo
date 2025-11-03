#!/usr/bin/env python3
"""
Test script for Regional News API
Tests Guangdong news and analyzes available sources and content
"""

import requests
import json
import os
from collections import Counter
from urllib.parse import urlparse

# Read API key from apikey.md file
API_KEY_PATH = os.path.join(os.path.dirname(__file__), 'apikey.md')
try:
    with open(API_KEY_PATH, 'r') as f:
        API_KEY = f.read().strip()
except FileNotFoundError:
    raise FileNotFoundError(f"API key file not found at {API_KEY_PATH}. Please create apikey.md with your API key.")

API_URL = "https://apis.tianapi.com/areanews/index"
REGION = "广东"

def test_api(page=1, keyword=None):
    """Test the API with Guangdong news"""
    params = {
        "key": API_KEY,
        "areaname": REGION,
        "page": page
    }
    
    if keyword:
        params["word"] = keyword
    
    print(f"\n{'='*60}")
    print(f"Testing API - Page {page}")
    print(f"Region: {REGION}")
    if keyword:
        print(f"Keyword: {keyword}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Code: {data.get('code')}")
        print(f"Message: {data.get('msg')}\n")
        
        if data.get('code') == 200:
            result = data.get('result', {})
            # Handle different response structures
            if isinstance(result, dict):
                articles = result.get('list', [])
            elif isinstance(result, list):
                articles = result
            else:
                articles = []
            
            print(f"Number of articles: {len(articles)}\n")
            
            # Analyze sources
            sources = [article.get('source', 'Unknown') for article in articles]
            source_counts = Counter(sources)
            
            print("=" * 60)
            print("SOURCE ANALYSIS")
            print("=" * 60)
            print(f"\nTotal unique sources: {len(source_counts)}")
            print(f"\nSources and their article counts:")
            for source, count in source_counts.most_common():
                print(f"  - {source}: {count} article(s)")
            
            # Analyze content availability
            print("\n" + "=" * 60)
            print("CONTENT ANALYSIS")
            print("=" * 60)
            
            articles_with_description = sum(1 for a in articles if a.get('description'))
            articles_with_pic = sum(1 for a in articles if a.get('picUrl'))
            articles_with_url = sum(1 for a in articles if a.get('url'))
            
            print(f"\nArticles with description: {articles_with_description}/{len(articles)}")
            print(f"Articles with image: {articles_with_pic}/{len(articles)}")
            print(f"Articles with URL: {articles_with_url}/{len(articles)}")
            
            # Sample articles
            print("\n" + "=" * 60)
            print("SAMPLE ARTICLES (First 3)")
            print("=" * 60)
            
            for i, article in enumerate(articles[:3], 1):
                print(f"\n--- Article {i} ---")
                print(f"ID: {article.get('id')}")
                print(f"Title: {article.get('title', 'N/A')}")
                print(f"Source: {article.get('source', 'N/A')}")
                print(f"Time: {article.get('ctime', 'N/A')}")
                print(f"Description: {article.get('description', 'N/A')[:100]}..." if article.get('description') else "Description: (empty)")
                print(f"Has Image: {'Yes' if article.get('picUrl') else 'No'}")
                print(f"URL: {article.get('url', 'N/A')}")
                
                # Check if URL is accessible
                if article.get('url'):
                    url = article.get('url')
                    try:
                        url_response = requests.head(url, timeout=5, allow_redirects=True)
                        print(f"URL Status: {url_response.status_code}")
                    except:
                        print(f"URL Status: Could not verify")
            
            return {
                'success': True,
                'articles': articles,
                'sources': list(source_counts.keys()),
                'source_counts': dict(source_counts),
                'total_articles': len(articles),
                'articles_with_description': articles_with_description,
                'articles_with_url': articles_with_url
            }
        else:
            print(f"API Error: {data.get('msg')}")
            return {
                'success': False,
                'error': data.get('msg'),
                'code': data.get('code')
            }
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return {'success': False, 'error': str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return {'success': False, 'error': 'Invalid JSON response'}

def check_fulltext_availability(keyword=None):
    """Check if full text can be retrieved from article URLs"""
    print("\n" + "=" * 60)
    print("FULL TEXT AVAILABILITY CHECK")
    print("=" * 60)
    
    result = test_api(page=1, keyword=keyword)
    
    if not result.get('success'):
        return result
    
    articles = result['articles']
    print(f"\nChecking {min(3, len(articles))} sample URLs for full text availability...\n")
    
    fulltext_info = []
    for article in articles[:3]:
        url = article.get('url')
        if not url:
            continue
        
        info = {
            'title': article.get('title'),
            'source': article.get('source'),
            'url': url,
            'has_description': bool(article.get('description')),
            'description_length': len(article.get('description', '')),
            'url_accessible': False,
            'content_type': None
        }
        
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            info['url_accessible'] = response.status_code == 200
            info['status_code'] = response.status_code
            info['content_type'] = response.headers.get('Content-Type', 'Unknown')
        except Exception as e:
            info['error'] = str(e)
        
        fulltext_info.append(info)
        print(f"  - {info['title'][:50]}...")
        print(f"    Source: {info['source']}")
        print(f"    URL accessible: {info['url_accessible']}")
        print(f"    Description length: {info['description_length']} chars")
        print()
    
    return {
        'articles': fulltext_info,
        'sources': result['sources'],
        'source_counts': result['source_counts']
    }

def comprehensive_source_search():
    """Search comprehensively to find all available sources"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SOURCE SEARCH")
    print("=" * 60)
    
    all_sources = set()
    all_source_counts = Counter()
    total_articles_scanned = 0
    
    # 1. Regular search without keyword (multiple pages)
    print("\n" + "=" * 60)
    print("1. REGULAR SEARCH (No Keyword)")
    print("=" * 60)
    
    for page in range(1, 6):  # Check pages 1-5
        result = test_api(page=page)
        if result.get('success'):
            sources = result['sources']
            all_sources.update(sources)
            all_source_counts.update(sources)
            total_articles_scanned += result['total_articles']
        else:
            break  # Stop if API fails
    
    print(f"\nRegular search found {len(all_sources)} unique sources")
    
    # 2. Keyword search with "展览"
    print("\n" + "=" * 60)
    print("2. KEYWORD SEARCH: 展览")
    print("=" * 60)
    
    keyword = "展览"
    keyword_sources = set()
    
    for page in range(1, 6):
        result = test_api(page=page, keyword=keyword)
        if result.get('success'):
            sources = result['sources']
            keyword_sources.update(sources)
            all_sources.update(sources)
            all_source_counts.update(sources)
            total_articles_scanned += result['total_articles']
        else:
            break
    
    print(f"\nKeyword search found {len(keyword_sources)} unique sources")
    if keyword_sources:
        print("Sources from keyword search:")
        for source in sorted(keyword_sources):
            print(f"  - {source}")
    
    # 3. Try a few more common keywords to find different sources
    additional_keywords = ["旅游", "经济", "科技", "教育"]
    
    print("\n" + "=" * 60)
    print("3. ADDITIONAL KEYWORD SEARCHES")
    print("=" * 60)
    
    for kw in additional_keywords:
        print(f"\nSearching with keyword: {kw}")
        kw_sources = set()
        for page in range(1, 3):  # Check 2 pages per keyword
            result = test_api(page=page, keyword=kw)
            if result.get('success'):
                sources = result['sources']
                kw_sources.update(sources)
                all_sources.update(sources)
                all_source_counts.update(sources)
                total_articles_scanned += result['total_articles']
            else:
                break
        print(f"  Found {len(kw_sources)} unique source(s): {', '.join(sorted(kw_sources)) if kw_sources else 'None'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SOURCE SUMMARY")
    print("=" * 60)
    print(f"\nTotal unique sources found: {len(all_sources)}")
    print(f"Total articles scanned: {total_articles_scanned}")
    print(f"\nAll sources and article counts:")
    for source, count in all_source_counts.most_common():
        print(f"  - {source}: {count} article(s)")
    
    return {
        'all_sources': sorted(all_sources),
        'source_counts': dict(all_source_counts),
        'total_articles': total_articles_scanned
    }

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("REGIONAL NEWS API TEST - GUANGDONG")
    print("=" * 60)
    
    # Comprehensive search
    summary = comprehensive_source_search()
    
    # Detailed test with keyword "展览"
    print("\n" + "=" * 60)
    print("DETAILED TEST WITH KEYWORD: 展览")
    print("=" * 60)
    result = test_api(page=1, keyword="展览")
    
    if result.get('success') and result['articles']:
        print("\nSample articles with keyword '展览':")
        for i, article in enumerate(result['articles'][:5], 1):
            print(f"\n{i}. {article.get('title')}")
            print(f"   Source: {article.get('source')}")
            print(f"   Time: {article.get('ctime')}")
    
    # Check full text availability
    fulltext_result = check_fulltext_availability(keyword="展览")

