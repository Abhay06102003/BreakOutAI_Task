FROM python:3.10-slim

# Set working directory in container
WORKDIR /

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip3 install --no-cache-dir -r requirements.txt

# Add these lines to your Dockerfile
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('stopwords');nltk.download('punkt_tab');nltk.download('averaged_perceptron_tagger_eng')"

# Copy the rest of the application code
COPY . .

# Expose port 5001 (assuming Flask or similar web app)
EXPOSE 5001  

# Command to run the application
CMD ["python", "app.py"]