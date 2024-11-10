import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation
import re

def extract_keywords(question, num_keywords=5):
    """
    Extract keywords from a question using basic NLP techniques.
    
    Args:
        question (str): Input question text
        num_keywords (int): Number of keywords to return
        
    Returns:
        list: List of extracted keywords
    """
    # Download required NLTK data (uncomment first time)
    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('averaged_perceptron_tagger')
    
    # Convert to lowercase and remove special characters
    question = re.sub(r'[^\w\s]', '', question.lower())
    
    # Tokenize the text
    tokens = word_tokenize(question)
    
    # Get English stop words
    stop_words = set(stopwords.words('english'))
    
    # Add common question words to stop words
    question_words = {'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 
                     'why', 'how', 'is', 'are', 'was', 'were', 'will', 'would'}
    stop_words.update(question_words)
    
    # Remove stop words and single characters
    keywords = [word for word in tokens if word not in stop_words and len(word) > 1]
    
    # Part of speech tagging
    pos_tags = nltk.pos_tag(keywords)
    
    # Prioritize nouns and verbs
    important_words = [word for word, pos in pos_tags if pos.startswith(('NN', 'VB', 'JJ'))]
    
    # If we don't have enough important words, add other non-stop words
    if len(important_words) < num_keywords:
        remaining_words = [w for w in keywords if w not in important_words]
        important_words.extend(remaining_words[:num_keywords - len(important_words)])
    
    return important_words[:num_keywords]

