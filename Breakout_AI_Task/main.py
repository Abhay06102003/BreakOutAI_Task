from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
from typing import List, Dict, Optional
from tqdm import tqdm
import logging
import pickle
import hashlib
from functools import lru_cache

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
        cache_dir: str = "cache",
        batch_size: int = 100
    ):
        """
        Initialize the AllInOne processor.

        Args:
            csv_path (str): Path to the input CSV file
            column (str): Name of the column to process
            question (str): Question to be answered
            max_workers (int, optional): Maximum number of parallel workers. Defaults to 3.
            cache_dir (str, optional): Directory for caching results. Defaults to "cache".
            batch_size (int, optional): Size of batches for batch processing. Defaults to 100.
        """
        self.csv = pd.read_csv(csv_path)
        self.column = list(self.csv[column])
        self.question = question
        self.max_workers = max_workers
        self.cache_dir = cache_dir
        self.batch_size = batch_size
        
        # Pre-compute keywords once instead of for each search
        self.suffix = ' '.join(extract_keywords(self.question))
        self.searches = [f"{text} {self.suffix}" for text in self.column]

    def _setup_cache(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    @lru_cache(maxsize=1000)  # Add memory-based caching
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

    def _process_batch(self, searches: List[str]) -> List[str]:
        """Process a batch of searches in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self._process_single_search, searches))

    def __call__(self) -> None:
        """Execute the parallel processing pipeline with batching."""
        logging.info("Starting batch processing")
        
        try:
            answers = []
            for i in range(0, len(self.searches), self.batch_size):
                batch = self.searches[i:i + self.batch_size]
                batch_answers = self._process_batch(batch)
                answers.extend(batch_answers)
                
                # Optional: Save intermediate results
                self.csv['answers'] = answers + [''] * (len(self.searches) - len(answers))
                self.csv.to_csv('intermediate_results.csv', index=False)
                
            self.csv['answers'] = answers
            
        except Exception as e:
            logging.error(f"Batch processing failed: {str(e)}")
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

def main():
    """
    Test function to demonstrate the usage of AllInOne class.
    """
    # Test parameters
    csv_path = "testing.csv"  # Replace with your actual CSV path
    column_name = "company"          # Replace with your actual column name
    question = "Give me the name of CEO of the company?"
    
    try:
        # Initialize the processor
        processor = AllInOne(
            csv_path=csv_path,
            column=column_name,
            question=question,
            max_workers=3,
            batch_size=50
        )
        
        # Process the data
        logging.info("Starting processing...")
        processor()
        
        # Save results
        processor.save_results("results.csv")
        
        # Display some results
        results_df = processor.get_results_as_dataframe()
        print("\nFirst few results:")
        print(results_df[['company', 'answers']].head())
        
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()