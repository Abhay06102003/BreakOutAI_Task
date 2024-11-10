from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
from typing import List, Dict, Optional
from tqdm import tqdm
import logging
import pickle
import hashlib

from Keyword_extractor import extract_keywords
from WebScrapper import extract_top_website_text
from kg import KG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class AllInOne:
    """
    A class that processes search queries in parallel, extracts information, and manages results.
    
    This class handles:
    - Keyword extraction from questions
    - Web scraping for relevant information
    - Knowledge graph querying
    - Result caching
    - Parallel processing of searches
    """

    def __init__(
        self, 
        csv_path: str, 
        column: str, 
        question: str, 
        max_workers: int = 3,
        cache_dir: str = "cache"
    ):
        """
        Initialize the AllInOne processor.

        Args:
            csv_path (str): Path to the input CSV file
            column (str): Name of the column to process
            question (str): Question to be answered
            max_workers (int, optional): Maximum number of parallel workers. Defaults to 3.
            cache_dir (str, optional): Directory for caching results. Defaults to "cache".
        """
        self.csv = pd.read_csv(csv_path)
        self.column = list(self.csv[column])
        self.question = question
        self.max_workers = max_workers
        self.cache_dir = cache_dir
        self._setup_cache()
        
        logging.info("Extracting keywords from question")
        suffix = ' '.join(extract_keywords(self.question))
        self.searches = [f"{text} {suffix}" for text in self.column]

    def _setup_cache(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_filename(self, search: str) -> str:
        """
        Generate a stable cache filename from search string.

        Args:
            search (str): Search query string

        Returns:
            str: Cache filename
        """
        hash_object = hashlib.md5(search.encode())
        return os.path.join(self.cache_dir, f"search_{hash_object.hexdigest()[:10]}.pkl")

    def _process_single_search(self, search: str) -> str:
        """
        Process a single search query with caching.

        Args:
            search (str): Search query to process

        Returns:
            str: Response from knowledge graph or error message
        """
        cache_file = self._get_cache_filename(search)
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            logging.info(f"Using cached result for: {search}")
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logging.warning(f"Cache load failed for {search}: {str(e)}")
        
        # Process if not in cache
        try:
            logging.info(f"Processing search: {search}")
            extract_top_website_text(search, 3)
            
            knowledge_g = KG('data')
            response = knowledge_g.query(self.question)
            
            # Cleanup
            data_file = f"data/{search}.md"
            if os.path.exists(data_file):
                os.remove(data_file)
            
            # Cache the result
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(response, f)
            except Exception as e:
                logging.error(f"Failed to cache result for {search}: {str(e)}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing {search}: {str(e)}"
            logging.error(error_msg)
            return error_msg

    def __call__(self) -> None:
        """Execute the parallel processing pipeline."""
        logging.info("Starting parallel processing")
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                answers = list(tqdm(
                    executor.map(self._process_single_search, self.searches),
                    total=len(self.searches),
                    desc="Processing searches"
                ))
            
            self.csv['answers'] = answers
            
        except Exception as e:
            logging.error(f"Parallel processing failed: {str(e)}")
            raise

    def get_results_as_dataframe(self) -> pd.DataFrame:
        """
        Get the results as a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the results
        """
        return self.csv

    def save_results(self, output_path: str) -> None:
        """
        Save results to CSV file.

        Args:
            output_path (str): Path where to save the CSV file

        Raises:
            Exception: If saving fails
        """
        try:
            self.csv.to_csv(output_path, index=False)
            logging.info(f"Results saved to {output_path}")
        except Exception as e:
            logging.error(f"Failed to save results: {str(e)}")
            raise