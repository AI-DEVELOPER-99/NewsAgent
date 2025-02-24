import httpx
from bs4 import BeautifulSoup
from transformers import pipeline
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_model():
    global summarizer
    logging.info("Loading summarization model in a separate thread. This may take some time...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    logging.info("Model loaded successfully.")

model_thread = threading.Thread(target=load_model)
model_thread.start()

# Function to fetch article content from a link
def fetch_article_content(link):
    try:
        with httpx.Client() as client:
            response = client.get(link)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Failed to retrieve the article. Error: {e}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the main article content (adjust based on the website's structure)
    article_content = ""
    for paragraph in soup.find_all('p'):  # Look for <p> tags containing text
        article_content += paragraph.text.strip() + " "

    return article_content.strip()

# Function to generate a summary using an LLM
def generate_summary(text, max_length=150):
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']

