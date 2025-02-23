import httpx
from bs4 import BeautifulSoup
from transformers import pipeline

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
    # Load a pre-trained summarization model
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Generate the summary
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# Example usage
if __name__ == "__main__":
    # Example news article link
    article_link = "https://www.indiatoday.in/movies/bollywood/story/pm-modi-says-chhaava-ki-dhoom-machi-hui-hai-as-he-praises-vicky-kaushal-laxman-utekar-film-2683650-2025-02-21"

    # Fetch the article content
    article_content = fetch_article_content(article_link)
    if article_content:
        print("Article Content:")
        print(article_content)
        print("-" * 50)

        # Generate a summary
        summary = generate_summary(article_content)
        print("Generated Summary:")
        print(summary)
    else:
        print("Failed to fetch article content.")