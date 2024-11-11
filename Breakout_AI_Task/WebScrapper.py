import os
import re
from dotenv import load_dotenv
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
from random import uniform
import logging
from typing import List, Dict
import lxml

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Cache for preprocessed text
TEXT_CACHE = {}

def preprocess_text(text: str) -> str:
    """Preprocesses text with caching"""
    cache_key = hash(text)
    if cache_key in TEXT_CACHE:
        return TEXT_CACHE[cache_key]
    
    # Combine all regex operations into one pass
    text = re.sub(
        r'(<[^>]+>)|(http\S+)|[^a-zA-Z\s]',
        ' ',
        text.lower()
    ).strip()
    text = ' '.join(text.split())
    
    TEXT_CACHE[cache_key] = text
    return text

async def extract_text_from_url(url: str, session: aiohttp.ClientSession) -> str:
    """Asynchronously extracts text from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with session.get(url, headers=headers, timeout=5) as response:
            if response.status != 200:
                return ""
                
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')

            # Remove unwanted elements in one pass
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()

            # Extract text more efficiently
            text_content = ' '.join(
                element.get_text()
                for element in soup.find_all(['p', 'article', 'section', 'div'])
            )
            
            return preprocess_text(text_content)
            
    except Exception as e:
        logging.error(f"Error extracting text from {url}: {str(e)}")
        return ""

async def extract_top_website_text(keyword: str, top_n: int, session: aiohttp.ClientSession) -> List[Dict[str, str]]:
    """Asynchronously extracts text from top search results"""
    try:
        encoded_keyword = quote(keyword)
        search_url = f"https://www.google.com/search?q={encoded_keyword}&num={top_n+5}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with session.get(search_url, headers=headers) as response:
            if response.status != 200:
                return []
                
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract URLs more efficiently
            urls = [
                link['href']
                for link in soup.select('div.g a')
                if link.get('href', '').startswith('http')
            ][:top_n]
            
            # Process URLs concurrently
            tasks = [
                extract_text_from_url(url, session)
                for url in urls
            ]
            contents = await asyncio.gather(*tasks)
            
            # Create results and filter empty contents
            website_contents = [
                {'url': url, 'content': content}
                for url, content in zip(urls, contents)
                if content
            ]
            
            await save_to_markdown(website_contents, keyword)
            return website_contents
            
    except Exception as e:
        logging.error(f"Error during search: {str(e)}")
        return []

async def save_to_markdown(data: List[Dict[str, str]], keyword: str) -> str:
    """Asynchronously saves data to markdown"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filename = f"data/{keyword}.md"
    
    # Build content string efficiently
    content_parts = [
        f"# Search Results for: {keyword}\n",
        f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    ]
    
    for idx, result in enumerate(data, 1):
        content_parts.extend([
            f"## Website {idx}\n",
            f"URL: {result['url']}\n\n",
            f"### Content:\n{result['content']}\n\n",
            "---\n\n"
        ])
    
    markdown_content = ''.join(content_parts)
    
    # Use async file operations
    async with aiohttp.ClientSession() as session:
        async with aiohttp.StreamWriter(filename, 'w', encoding='utf-8') as file:
            await file.write(markdown_content)
    
    logging.info(f"Data saved successfully to {filename}")
    return filename

# Example usage
async def main():
    async with aiohttp.ClientSession() as session:
        keyword = "artificial intelligence"
        num_results = 3
        results = await extract_top_website_text(keyword, num_results, session)
        print(f"Processed {len(results)} results")

if __name__ == "__main__":
    asyncio.run(main())