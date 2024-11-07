import os
import re
from dotenv import load_dotenv
from scraperapi_sdk import ScraperAPIClient
from bs4 import BeautifulSoup
import requests

load_dotenv()

def preprocess_text(text):
    """
    Preprocesses the given text to clean and normalize it.

    Args:
        text (str): The text to be preprocessed.

    Returns:
        str: The preprocessed text.
    """
    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text

def extract_text_from_url(client, url):
    """
    Extracts the main text content from a given URL.

    Args:
        client: ScraperAPI client instance
        url (str): The URL to extract text from

    Returns:
        str: Extracted and preprocessed text content
    """
    try:
        # Use ScraperAPI to get the webpage content
        response = client.get(url=url)

        # Parse the HTML content
        soup = BeautifulSoup(response, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()

        # Extract text from paragraphs and other relevant tags
        text_elements = soup.find_all(['p', 'article', 'section', 'div'])
        text_content = ' '.join(element.get_text() for element in text_elements)
        
        # Preprocess the extracted text
        return preprocess_text(text_content)
    except Exception as e:
        print(f"Error extracting text from {url}: {str(e)}")
        return ""

def extract_top_website_text(keyword,top_n):
    """
    Extracts the full text content from the top 4 search results for the given keyword.

    Args:
        keyword (str): The keyword to search for.

    Returns:
        list: A list of dictionaries containing website URLs and their preprocessed text content.
    """
    client = ScraperAPIClient(os.getenv("SCRAPER_API_KEY"))

    # First, get the search results
    search_url = f"https://www.google.com/search?q={keyword}&num={top_n}"
    search_response = client.get(url=search_url)
    
    # Parse the search results HTML
    soup = BeautifulSoup(search_response, 'html.parser')
    
    # Extract URLs from search results
    website_contents = []
    for result in soup.select('div.g'):
        link = result.find('a', href=True)
        if link:
            url = link['href']
            if url.startswith('http'):  # Ensure it's a valid URL
                # Extract full text content from the webpage
                content = extract_text_from_url(client, url)
                if content:
                    website_contents.append({
                        'url': url,
                        'content': content
                    })

    return website_contents

# Example usage
if __name__ == "__main__":
    keyword = "Artificial Intelligence"
    results = extract_top_website_text(keyword,2)
    
    for idx, result in enumerate(results, 1):
        print(f"\nWebsite {idx}:")
        print(f"URL: {result['url']}")
        print(f"Content preview: {result['content'][:500]}...")  # Show first 500 chars
        print("-" * 80)