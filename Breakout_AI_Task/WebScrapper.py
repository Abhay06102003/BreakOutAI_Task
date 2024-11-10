import os
import re
from dotenv import load_dotenv
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
from random import uniform

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
        # Add delay to avoid rate limiting
        time.sleep(uniform(1, 3))
        
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the webpage content
        response = session.get(url, headers=headers, timeout=30)
        response.html.render(timeout=30)  # Render JavaScript content

        # Parse the HTML content
        soup = BeautifulSoup(response.html.html, 'html.parser')

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
    search_url = f"https://www.google.com/search?q={encoded_keyword}&num={top_n}"
    
    try:
        # Add headers to mimic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get search results
        search_response = session.get(search_url, headers=headers)
        search_response.html.render(timeout=30)
        
        # Parse the search results HTML
        soup = BeautifulSoup(search_response.html.html, 'html.parser')
        
        # Extract URLs from search results
        website_contents = []
        for result in soup.select('div.g'):
            link = result.find('a', href=True)
            if link:
                url = link['href']
                if url.startswith('http'):  # Ensure it's a valid URL
                    # Extract full text content from the webpage
                    content = extract_text_from_url(session, url)
                    if content:
                        website_contents.append({
                            'url': url,
                            'content': content
                        })
                        
                    # Break if we have reached the desired number of results
                    if len(website_contents) >= top_n:
                        break
        
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