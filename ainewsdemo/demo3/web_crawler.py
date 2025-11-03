#!/usr/bin/env python3
"""
Web crawler to extract full text content from news article URLs
Supports multiple news sources: 南方网, 金羊网, 中国新闻网
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse
import time

class NewsCrawler:
    def __init__(self, timeout=10):
        """
        Initialize the crawler with default settings
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def fetch_url(self, url):
        """
        Fetch HTML content from URL
        
        Args:
            url: Article URL
            
        Returns:
            tuple: (success: bool, content: str or error message)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return True, response.text
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def identify_source(self, url):
        """Identify the news source from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'southcn.com' in domain or 'southcn' in domain:
            return 'southcn'  # 南方网
        elif 'ycwb.com' in domain:
            return 'ycwb'  # 金羊网
        elif 'chinanews.com.cn' in domain:
            return 'chinanews'  # 中国新闻网
        else:
            return 'unknown'
    
    def extract_southcn(self, soup, url):
        """Extract article content from 南方网 (Southcn.com)"""
        content = ""
        
        # Try different selectors for 南方网 articles
        selectors = [
            'div.article-content',
            'div.content',
            'div.article-body',
            'div[class*="content"]',
            'div[class*="article"]',
            'article',
            'div.text',
        ]
        
        for selector in selectors:
            article_content = soup.select_one(selector)
            if article_content:
                # Remove script and style elements
                for script in article_content(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                content = article_content.get_text(separator='\n', strip=True)
                if len(content) > 200:  # Only accept if substantial content
                    break
        
        # If no specific content found, try getting main text
        if not content or len(content) < 200:
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'})
            if main_content:
                for script in main_content(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                content = main_content.get_text(separator='\n', strip=True)
        
        return content
    
    def extract_ycwb(self, soup, url):
        """Extract article content from 金羊网 (Ycwb.com)"""
        content = ""
        
        selectors = [
            'div.article-content',
            'div.content',
            'div.article-body',
            'div[class*="content"]',
            'div[class*="article"]',
            'article',
            'div.text',
            'div.main-content',
        ]
        
        for selector in selectors:
            article_content = soup.select_one(selector)
            if article_content:
                for script in article_content(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                content = article_content.get_text(separator='\n', strip=True)
                if len(content) > 200:
                    break
        
        if not content or len(content) < 200:
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'})
            if main_content:
                for script in main_content(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                content = main_content.get_text(separator='\n', strip=True)
        
        return content
    
    def extract_chinanews(self, soup, url):
        """Extract article content from 中国新闻网 (China News Network)"""
        content = ""
        
        selectors = [
            'div.left_zw',
            'div.content',
            'div.article-content',
            'div[class*="content"]',
            'div[class*="article"]',
            'article',
            'div.text',
        ]
        
        for selector in selectors:
            article_content = soup.select_one(selector)
            if article_content:
                for script in article_content(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                content = article_content.get_text(separator='\n', strip=True)
                if len(content) > 200:
                    break
        
        if not content or len(content) < 200:
            main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'content'})
            if main_content:
                for script in main_content(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                content = main_content.get_text(separator='\n', strip=True)
        
        return content
    
    def extract_generic(self, soup, url):
        """Generic extraction method when source is unknown"""
        content = ""
        
        # Try common article tags and classes
        article = soup.find('article')
        if article:
            for script in article(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            content = article.get_text(separator='\n', strip=True)
        
        if not content or len(content) < 200:
            # Try main content areas
            main = soup.find('main') or soup.find('div', {'id': 'content'}) or soup.find('div', {'class': 'content'})
            if main:
                for script in main(["script", "style", "nav", "footer", "header", "aside"]):
                    script.decompose()
                content = main.get_text(separator='\n', strip=True)
        
        return content
    
    def extract_title(self, soup):
        """Extract article title"""
        title_selectors = [
            'h1',
            'title',
            'h1.article-title',
            'div.title',
            'h1[class*="title"]',
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return ""
    
    def extract_metadata(self, soup, url):
        """Extract metadata like author, publish date"""
        metadata = {
            'author': '',
            'publish_date': '',
            'source_url': url,
        }
        
        # Try to find author
        author_selectors = [
            'span.author',
            'div.author',
            'p.author',
            '[class*="author"]',
            '[class*="byline"]',
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                metadata['author'] = author_elem.get_text(strip=True)
                break
        
        # Try to find publish date
        date_selectors = [
            'span.date',
            'div.date',
            'p.date',
            'time',
            '[class*="date"]',
            '[class*="time"]',
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                metadata['publish_date'] = date_elem.get_text(strip=True)
                break
        
        return metadata
    
    def crawl_article(self, url):
        """
        Crawl and extract full text from an article URL
        
        Args:
            url: Article URL
            
        Returns:
            dict: Extraction results with content and metadata
        """
        result = {
            'url': url,
            'success': False,
            'source': self.identify_source(url),
            'title': '',
            'content': '',
            'content_length': 0,
            'metadata': {},
            'error': None,
        }
        
        print(f"\n{'='*60}")
        print(f"Crawling: {url}")
        print(f"Source: {result['source']}")
        print(f"{'='*60}")
        
        # Fetch URL
        success, html_content = self.fetch_url(url)
        if not success:
            result['error'] = html_content
            return result
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            result['error'] = f"HTML parsing error: {str(e)}"
            return result
        
        # Extract title
        result['title'] = self.extract_title(soup)
        
        # Extract content based on source
        if result['source'] == 'southcn':
            result['content'] = self.extract_southcn(soup, url)
        elif result['source'] == 'ycwb':
            result['content'] = self.extract_ycwb(soup, url)
        elif result['source'] == 'chinanews':
            result['content'] = self.extract_chinanews(soup, url)
        else:
            result['content'] = self.extract_generic(soup, url)
        
        # Extract metadata
        result['metadata'] = self.extract_metadata(soup, url)
        result['content_length'] = len(result['content'])
        
        # Check if extraction was successful
        if result['content'] and len(result['content']) > 100:
            result['success'] = True
            print(f"✓ Successfully extracted {result['content_length']} characters")
        else:
            result['error'] = f"Extracted content too short ({result['content_length']} chars)"
            print(f"✗ Extraction failed: {result['error']}")
        
        return result

def get_test_urls_from_api():
    """Get test URLs from the API"""
    # Read API key
    api_key_path = os.path.join(os.path.dirname(__file__), 'apikey.md')
    try:
        with open(api_key_path, 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("Warning: API key file not found. Using hardcoded test URLs.")
        return []
    
    # Get articles from API
    import requests
    api_url = "https://apis.tianapi.com/areanews/index"
    params = {
        "key": api_key,
        "areaname": "广东",
        "page": 1
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        
        if data.get('code') == 200:
            result = data.get('result', {})
            if isinstance(result, dict):
                articles = result.get('list', [])
            elif isinstance(result, list):
                articles = result
            else:
                articles = []
            
            # Get URLs from different sources
            urls = []
            sources_seen = set()
            
            for article in articles:
                url = article.get('url')
                source = article.get('source', '')
                
                if url and source not in sources_seen:
                    urls.append((url, source))
                    sources_seen.add(source)
                    if len(urls) >= 5:  # Get up to 5 URLs
                        break
            
            # Also try keyword search for more variety
            params['word'] = '展览'
            response2 = requests.get(api_url, params=params, timeout=10)
            data2 = response2.json()
            
            if data2.get('code') == 200:
                result2 = data2.get('result', {})
                if isinstance(result2, dict):
                    articles2 = result2.get('list', [])
                elif isinstance(result2, list):
                    articles2 = result2
                else:
                    articles2 = []
                
                for article in articles2:
                    url = article.get('url')
                    source = article.get('source', '')
                    if url and source not in sources_seen:
                        urls.append((url, source))
                        sources_seen.add(source)
                        if len(urls) >= 8:
                            break
            
            return [url for url, _ in urls]
    except Exception as e:
        print(f"Error fetching URLs from API: {e}")
        return []
    
    return []

def main():
    """Main function to test the crawler"""
    print("\n" + "="*60)
    print("NEWS ARTICLE WEB CRAWLER TEST")
    print("="*60)
    
    crawler = NewsCrawler(timeout=15)
    
    # Get test URLs
    print("\nFetching test URLs from API...")
    test_urls = get_test_urls_from_api()
    
    # Fallback URLs if API fails
    if not test_urls:
        print("Using fallback test URLs...")
        test_urls = [
            "https://xapp.southcn.com/node_2ea31fe5fd/b150021036.shtml",  # 南方网
            "https://news.ycwb.com/ikinvjktjn/content_53731774.htm",  # 金羊网
            "http://www.gd.chinanews.com.cn/2025/2025-03-02/440615.shtml",  # 中国新闻网
        ]
    
    print(f"Testing {len(test_urls)} URLs...\n")
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}]")
        result = crawler.crawl_article(url)
        results.append(result)
        
        # Print summary
        if result['success']:
            print(f"Title: {result['title'][:60]}...")
            print(f"Content preview: {result['content'][:150]}...")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("CRAWLING SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r['success'])
    total_length = sum(r['content_length'] for r in results if r['success'])
    
    print(f"\nTotal URLs tested: {len(results)}")
    print(f"Successful extractions: {successful}/{len(results)}")
    print(f"Total content extracted: {total_length:,} characters")
    
    print(f"\nDetailed results:")
    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"\n{status} [{i}] {result['source']}")
        print(f"   URL: {result['url'][:70]}...")
        print(f"   Title: {result['title'][:50]}...")
        print(f"   Content length: {result['content_length']:,} chars")
        if result['error']:
            print(f"   Error: {result['error']}")
    
    # Save results to file
    output_file = 'crawler_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    
    return results

if __name__ == "__main__":
    main()

