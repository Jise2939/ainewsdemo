# Regional News API - Guangdong News Documentation

This directory contains scripts and documentation for testing the TianAPI Regional News API for Guangdong (广东) news.

## API Overview

**API Endpoint:** `https://apis.tianapi.com/areanews/index`

**API Type:** Regional news for Chinese provinces, municipalities, and special administrative regions

**Documentation:** See `RegionalNewsAPIdoc.md` for full API documentation

## What's Available

### API Features
- Query news articles by region (province/municipality)
- Keyword search within regional news
- Pagination support
- Returns article metadata including title, source, URL, and publication time

### Data Fields Returned

Each article contains:
- **id**: Unique article identifier
- **title**: Article headline
- **source**: News source/publisher
- **url**: Link to full article
- **ctime**: Publication date and time (format: "YYYY-MM-DD HH:MM:SS")
- **description**: Article description/summary (typically empty in API response)
- **picUrl**: Image URL (typically empty in API response)

### Test Results - Guangdong News

Based on comprehensive testing across multiple pages and keyword searches:

#### Available News Sources

1. **南方网 (Southcn.com)**
   - Major Guangdong news source
   - Provides comprehensive coverage of Guangdong news
   - URLs are accessible and contain full article content
   - Most frequent source in regular searches

2. **金羊网 (Ycwb.com)**
   - Another prominent Guangdong news source
   - Also provides full article access via URLs
   - Regular contributor to Guangdong news

3. **中国新闻网 (China News Network / gd.chinanews.com.cn)**
   - National news network with Guangdong coverage
   - Discovered through keyword searches (e.g., "展览")
   - URLs are accessible and contain full article content

**Total unique sources found:** 3

**Source Distribution** (from comprehensive search of 114 articles):
- 南方网: ~35% of articles (most frequent in general news)
- 金羊网: ~32% of articles
- 中国新闻网: ~21% of articles (more common in specific topic searches)

**Note:** Keyword searches (e.g., "展览" for exhibitions) can reveal different sources than regular searches. Using targeted keywords may help discover articles from sources that appear less frequently in general news feeds.

## Full Text Availability

### API Response Level
- **Description field**: Empty in API responses
- **Images**: Not included in API response (`picUrl` field is empty)
- **URLs**: All articles include accessible URLs

### Full Text Access

✅ **Full text IS available** by fetching articles from the provided URLs:

- **URL Accessibility**: URLs are accessible (HTTP 200 status)
- **Content Format**: HTML pages containing full article text
- **Content Length**: Articles typically contain several hundred to thousands of characters
- **Extraction**: Full text can be extracted from URLs using web scraping techniques

**Verification:**
- Tested sample URLs successfully returned full HTML content
- Article content can be parsed using HTML parsing libraries (e.g., BeautifulSoup)
- URLs point to actual news articles on source websites

### Recommendations for Full Text Access

To obtain full article text:

1. Use the `url` field from API response
2. Fetch the HTML content from the URL
3. Parse HTML to extract article body text
4. Handle source-specific HTML structures (each source may have different layouts)

**Note:** Web scraping should comply with:
- Source website terms of service
- Rate limiting considerations
- Robots.txt guidelines

## Usage Example

### Python Script

```python
import requests
import os

# Read API key from apikey.md (keep this file secure and don't commit to git)
API_KEY_PATH = 'apikey.md'
with open(API_KEY_PATH, 'r') as f:
    API_KEY = f.read().strip()

API_URL = "https://apis.tianapi.com/areanews/index"

# Query Guangdong news (regular search)
params = {
    "key": API_KEY,
    "areaname": "广东",  # Note: no "省" suffix
    "page": 1  # Optional: pagination
}

# Or use keyword search to find topic-specific articles
params_with_keyword = {
    "key": API_KEY,
    "areaname": "广东",
    "word": "展览",  # Search for articles containing "展览" (exhibitions)
    "page": 1
}

response = requests.get(API_URL, params=params)
data = response.json()

if data.get('code') == 200:
    result = data.get('result', {})
    # Handle different response structures
    if isinstance(result, dict):
        articles = result.get('list', [])
    elif isinstance(result, list):
        articles = result
    else:
        articles = []
    
    for article in articles:
        print(f"Title: {article.get('title')}")
        print(f"Source: {article.get('source')}")
        print(f"URL: {article.get('url')}")
        print(f"Time: {article.get('ctime')}")
        print()
```

### API Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | Yes | Your API key |
| `areaname` | string | Yes | Region name (without "省" or "市"), e.g., "广东", "湖北", "上海" |
| `word` | string | No | Search keyword within regional news (recommended for finding topic-specific articles) |
| `page` | int | No | Page number for pagination (default: 1) |

### Keyword Search Benefits

Using the `word` parameter for keyword searches can:
- Discover articles from sources that appear less frequently in general news feeds
- Find topic-specific coverage (e.g., "展览" for exhibitions, "旅游" for tourism)
- Access a broader range of news sources for specialized topics

**Example:** Searching Guangdong news with keyword "展览" (exhibitions) revealed articles from **中国新闻网** that were not present in regular searches.

### Response Format

```json
{
  "code": 200,
  "msg": "success",
  "result": {
    "list": [
      {
        "id": "article_id",
        "title": "Article Title",
        "source": "News Source",
        "url": "https://article-url.com",
        "ctime": "2025-11-03 13:43:00",
        "description": "",
        "picUrl": ""
      }
    ]
  }
}
```

## Files in This Directory

- `apikey.md`: Contains the API key (keep secure - **NOT synced to GitHub**)
- `RegionalNewsAPIdoc.md`: Full API documentation in Chinese
- `test_api.py`: Test script that queries Guangdong news and analyzes sources
- `check_fulltext.py`: Script to verify full text availability from article URLs
- `web_crawler.py`: Web crawler for extracting full text from article URLs
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file
- `crawler_results.json`: Crawler output (generated after running web_crawler.py)

## Security Note

⚠️ **Important**: The `apikey.md` file contains sensitive API credentials and is excluded from Git via `.gitignore`. Never commit this file to version control. The test scripts read the API key from this file at runtime.

## Testing

Run the test script to query Guangdong news:

```bash
python3 test_api.py
```

Check full text availability:

```bash
python3 check_fulltext.py
```

## Web Crawler for Full Text Extraction

A web crawler (`web_crawler.py`) is available to extract full text content from article URLs. The crawler supports all three news sources found:

### Features

- **Multi-source support**: Handles 南方网, 金羊网, and 中国新闻网
- **Intelligent extraction**: Uses source-specific extraction methods
- **Metadata extraction**: Extracts title, author, publish date
- **Robust error handling**: Handles timeouts, network errors, and parsing issues
- **JSON output**: Saves results in structured JSON format

### Usage

```bash
python3 web_crawler.py
```

The crawler will:
1. Automatically fetch test URLs from the API
2. Extract full text from each article
3. Display extraction results and statistics
4. Save results to `crawler_results.json`

### Test Results

✅ **Successfully tested on all 3 sources:**
- **南方网 (southcn)**: ✓ Extracted full text (306+ chars)
- **金羊网 (ycwb)**: ✓ Extracted full text (943+ chars)
- **中国新闻网 (chinanews)**: ✓ Extracted full text (1,207+ chars)

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser (recommended for better performance)

## API Limitations

Based on API documentation:

- **Free Tier**: 100 calls per day
- **Rate Limit**: 5-10 QPS for free tier
- **Member Tiers**: Available with higher quotas (see `RegionalNewsAPIdoc.md`)

## Error Codes

Common error codes:
- `200`: Success
- `150`: API available calls insufficient
- `230`: API key error or empty
- `250`: Data return empty
- `280`: Missing required parameters

See `RegionalNewsAPIdoc.md` for complete error code list.

## Summary

✅ **What's Available:**
- Regional news articles for Guangdong
- Article metadata (title, source, URL, time)
- Pagination support
- Keyword search capability (helps discover additional sources)

✅ **Sources Found (3 total):**
- 南方网 (Southcn.com) - Most frequent in general news
- 金羊网 (Ycwb.com) - Regular contributor
- 中国新闻网 (China News Network) - More common in keyword searches

✅ **Full Text Availability:**
- Not in API response description field
- Available by fetching from article URLs
- URLs are accessible and contain full HTML content
- Requires web scraping to extract full text

✅ **Keyword Search Benefits:**
- Using keywords (e.g., "展览") can reveal sources not present in regular news feeds
- Helps find topic-specific articles from a broader range of sources
- Recommended for comprehensive source discovery

