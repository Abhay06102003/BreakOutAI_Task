import os
import re
from dotenv import load_dotenv
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
from random import uniform
import concurrent.futures
from functools import partial

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

def extract_text_from_url(session, url):
    """
    Extracts the main text content from a given URL.

    Args:
        session: HTMLSession instance
        url (str): The URL to extract text from

    Returns:
        str: Extracted and preprocessed text content
    """
    try:
        # Reduce sleep time and make it optional
        time.sleep(uniform(0.5, 1))
        
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the webpage content without JavaScript rendering
        response = session.get(url, headers=headers, timeout=10)  # Reduced timeout
        
        # Only render JavaScript if necessary (you can remove this if not needed)
        # response.html.render(timeout=10)

        soup = BeautifulSoup(response.text, 'lxml')  # Using lxml parser instead of html.parser

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

def extract_top_website_text(keyword, top_n):
    """
    Extracts the full text content from the top search results for the given keyword.

    Args:
        keyword (str): The keyword to search for.
        top_n (int): Number of top results to extract.

    Returns:
        list: A list of dictionaries containing website URLs and their preprocessed text content.
    """
    session = HTMLSession()
    
    # Encode the search query
    encoded_keyword = quote(keyword)
    
    # Google search URL
    search_url = f"https://www.google.com/search?q={encoded_keyword}&num={top_n+5}"  # Request extra results
    
    try:
        # Add headers to mimic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get search results
        search_response = session.get(search_url, headers=headers)
        # Remove JavaScript rendering for search results if possible
        # search_response.html.render(timeout=10)
        
        # Parse the search results HTML
        soup = BeautifulSoup(search_response.text, 'lxml')
        
        # Extract URLs first
        urls = []
        for result in soup.select('div.g'):
            link = result.find('a', href=True)
            if link and link['href'].startswith('http'):
                urls.append(link['href'])
        
        # Process URLs in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            extract_func = partial(extract_text_from_url, session)
            results = list(executor.map(extract_func, urls[:top_n]))
            
        website_contents = [
            {'url': url, 'content': content}
            for url, content in zip(urls[:top_n], results)
            if content  # Filter out empty results
        ]
        
        save_to_markdown(website_contents, keyword)
        return website_contents
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
    finally:
        session.close()

def save_to_markdown(data, keyword):
    """
    Saves the extracted data to a Markdown file.

    Args:
        data (list): The data to save
        keyword (str): The search keyword used
    """
    # Create 'data' directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create filename with timestamp
    filename = f"data/{keyword}.md"
    
    # Create the Markdown content
    markdown_content = f"# Search Results for: {keyword}\n\n"
    markdown_content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for idx, result in enumerate(data, 1):
        markdown_content += f"## Website {idx}\n"
        markdown_content += f"URL: {result['url']}\n\n"
        markdown_content += f"### Content:\n{result['content']}\n\n"
        markdown_content += "---\n\n"
    
    # Save the Markdown file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    
    print(f"Data saved successfully to {filename}")
    return filename

# if __name__ == "__main__":
#     keyword = "artificial intelligence"
#     num_results = 3
#     extract_top_website_text(keyword, num_results)