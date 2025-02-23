import httpx
from bs4 import BeautifulSoup
from transformers import pipeline
import time
from .summarizer import fetch_article_content
import json  # Add at the top

def save_articles_to_cache():
    global articles
    with open('cached_articles.json', 'w') as f:
        json.dump(articles, f)

def load_cached_articles():
    global articles
    try:
        with open('cached_articles.json', 'r') as f:
            articles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        articles = {}
    return articles

# In-memory storage for scraped articles
articles = []

# Define configurations for multiple news sites
sites_config = [
    {
        'name': 'India Today',
        'base_url': 'https://www.indiatoday.in',
        'article_tag': 'article',
        'article_class': 'B1S3_story__card__A_fhi',
        'headline_tag': 'h2',
        'summary_tag': 'p',
        'num_pages': 2  # Number of pages to scrape for this site
    },
    # {
    #     'name': 'BBC News',
    #     'base_url': 'https://www.bbc.com/news',
    #     'article_tag': 'div',
    #     'article_class': 'gs-c-promo',
    #     'headline_tag': 'h3',
    #     'summary_tag': 'p',
    #     'num_pages': 2  # Number of pages to scrape for this site
    # },
    # {
    #     'name': 'Reuters',
    #     'base_url': 'https://www.reuters.com/news/archive',
    #     'article_tag': 'article',
    #     'article_class': 'story',
    #     'headline_tag': 'h3',
    #     'summary_tag': 'p',
    #     'num_pages': 2  # Number of pages to scrape for this site
    # }
]

# Define broader topics and subcategories
broader_topics = {
    "World News": ["UK", "US", "Europe", "Asia", "Middle East"],
    "Sports": ["Football", "Cricket", "Tennis", "Olympics"],
    "Technology": ["Microsoft", "Apple", "AI", "Space"],
    "Entertainment": ["Movie", "Music", "Celebrity"]
}

# Function to fetch and parse news articles from a single page
def scrape_news_page(url, site_config):
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
    except httpx.HTTPError as e:
        print(f"Failed to retrieve the page. Error: {e}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract relevant information based on site-specific configuration
    scraped_articles = []
    for item in soup.find_all(site_config['article_tag'], class_=site_config['article_class']):
        headline = item.find(site_config['headline_tag']).text.strip() if item.find(site_config['headline_tag']) else "No headline"
        summary = item.find(site_config['summary_tag']).text.strip() if item.find(site_config['summary_tag']) else "No summary"
        link = item.find('a')['href'] if item.find('a') else "No link"
        image = item.find('img')['src'] if item.find('img') else None  # Extract image URL

        # Ensure the link and image URL are absolute (if relative, prepend the base URL)
        if not link.startswith('http'):
            link = httpx.URL(url).join(link)
        if image and not image.startswith('http'):
            image = httpx.URL(url).join(image)

        scraped_articles.append({
    'headline': headline,
    'summary': summary,
    'link': link,
    'image': image,
    'source': site_config['name'],
    'content': fetch_article_content(link) or "Content unavailable"  # Add this line
})

    return scraped_articles

# Function to scrape multiple pages for a single site
def scrape_site(base_url, site_config, num_pages):
    all_articles = []
    seen_links = set()  # Track unique article links

    for page in range(1, num_pages + 1):
        # Construct the URL for each page (e.g., https://www.indiatoday.in?page=2)
        page_url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"Scraping {site_config['name']}, page {page}: {page_url}")

        # Scrape the current page
        articles = scrape_news_page(page_url, site_config)
        if articles:
            for article in articles:
                if article['link'] not in seen_links:  # Check for duplicates
                    all_articles.append(article)
                    seen_links.add(article['link'])

        # Add a delay to avoid overwhelming the server
        time.sleep(2)  # Wait 2 seconds between requests

    return all_articles

# Function to classify articles into broader topics and subcategories
def classify_articles(articles):
    classified_articles = {topic: {} for topic in broader_topics}

    for article in articles:
        for topic, subcategories in broader_topics.items():
            for subcategory in subcategories:
                if subcategory.lower() in article['headline'].lower() or subcategory.lower() in article['summary'].lower():
                    if subcategory not in classified_articles[topic]:
                        classified_articles[topic][subcategory] = []
                    classified_articles[topic][subcategory].append(article)
                    break  # Stop checking other subcategories once a match is found

    return classified_articles

# Function to periodically scrape news websites
def automated_scraping():
    global articles
    load_cached_articles()  # Load existing cache on start
    while True:
        all_articles = []
        for site_config in sites_config:
            scraped_articles = scrape_site(site_config['base_url'], site_config, site_config['num_pages'])
            if scraped_articles:
                all_articles.extend(scraped_articles)
       
        # Classify articles
        classified_articles = classify_articles(all_articles)


        # Update the global articles list
        articles = classified_articles
        save_articles_to_cache()  # Save after each update
        time.sleep(600)
        print(f"Scraped and classified {len(all_articles)} articles.")

        # Wait for 10 minutes before scraping again
        time.sleep(600)

def get_articles():
    return articles

def get_broader_topics():
    return broader_topics