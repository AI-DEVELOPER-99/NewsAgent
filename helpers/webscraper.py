import httpx
from bs4 import BeautifulSoup
from transformers import pipeline
import time

# Function to fetch and parse news articles from a single page
def scrape_news_page(url, site_config):
    # Send a GET request to the URL using httpx
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
    articles = []
    for item in soup.find_all(site_config['article_tag'], class_=site_config['article_class']):
        headline = item.find(site_config['headline_tag']).text.strip() if item.find(site_config['headline_tag']) else "No headline"
        summary = item.find(site_config['summary_tag']).text.strip() if item.find(site_config['summary_tag']) else "No summary"
        link = item.find('a')['href'] if item.find('a') else "No link"
        image = item.find('img')['src'] if item.find('img') else None

        # Ensure the link is absolute (if relative, prepend the base URL)
        if not link.startswith('http'):
            link = httpx.URL(url).join(link)

        articles.append({
            'headline': headline,
            'summary': summary,
            'link': link,
            'image': image,
            'source': site_config['name']  # Add the source of the article
        })

    return articles

# Function to scrape multiple pages for a single site
def scrape_site(base_url, site_config, num_pages):
    all_articles = []
    seen_links = set()

    for page in range(1, num_pages + 1):
        # Construct the URL for each page (e.g., https://www.bbc.com/news?page=2)
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

# Function to classify articles into broader topics and sub-topics
def classify_articles(articles, broader_topic, sub_topic_keywords):
    classified_articles = []

    for article in articles:
        # Check if the article matches the sub-topic keywords
        if any(keyword.lower() in article['headline'].lower() or
               keyword.lower() in article['summary'].lower()
               for keyword in sub_topic_keywords):
            article['broader_topic'] = broader_topic
            article['sub_topic'] = ', '.join(sub_topic_keywords)
            classified_articles.append(article)

    return classified_articles

# Example usage
if __name__ == "__main__":
    # Define configurations for each news site
    sites_config = [
        {
            'name': 'India Today',
            'base_url': 'https://www.indiatoday.in',
            'article_tag': 'article',
            'article_class': 'B1S3_story__card__A_fhi',
            'headline_tag': 'h2',
            'summary_tag': 'p',
            'num_pages': 5  # Number of pages to scrape for this site
        }
    ]

    # Scrape articles from all sites
    all_articles = []
    for site_config in sites_config:
        articles = scrape_site(site_config['base_url'], site_config, site_config['num_pages'])
        if articles:
            all_articles.extend(articles)

    if all_articles:
        # Define broader topic and sub-topic keywords
        broader_topic = "World News"
        sub_topic_keywords = ["UK", "US", "Europe", 'Sports', 'Movie', 'Microsoft', 'India']

        # Classify articles
        classified_articles = classify_articles(all_articles, broader_topic, sub_topic_keywords)

        # Print the results
        print(f"Total articles scraped: {len(all_articles)}")
        print(f"Total classified articles: {len(classified_articles)}")
        print("-" * 50)
        for article in classified_articles:
            print(f"Source: {article['source']}")
            print(f"Headline: {article['headline']}")
            print(f"Summary: {article['summary']}")
            print(f"Link: {article['link']}")
            print(f"Broader Topic: {article['broader_topic']}")
            print(f"Sub-Topic: {article['sub_topic']}")
            print("-" * 50)
    else:
        print("No articles found.")