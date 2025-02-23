from flask import Flask, render_template
import httpx
from bs4 import BeautifulSoup
import threading
import time

from helpers.webscraper import scrape_site, classify_articles

app = Flask(__name__)

# # In-memory storage for scraped articles
articles = []

# Function to periodically scrape news websites
def automated_scraping():
    global articles
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

    broader_topic = "World News"
    sub_topic_keywords = ["UK", "US", "Europe", "Sports", "Movie", "Microsoft"]

    while True:
        all_articles = []
        for site_config in sites_config:
            articles = scrape_site(site_config['base_url'], site_config, site_config['num_pages'])
            if articles:
                all_articles.extend(articles)

        # Classify articles
        classified_articles = classify_articles(all_articles, broader_topic, sub_topic_keywords)

        # Update the global articles list
        articles = classified_articles
        print(f"Scraped {len(articles)} articles.")

        # Wait for 10 minutes before scraping again
        time.sleep(600)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html', articles=articles)

# Run the Flask app
if __name__ == '__main__':
    # Start the automated scraping thread
    scraping_thread = threading.Thread(target=automated_scraping)
    scraping_thread.daemon = True  # Daemonize thread to stop it when the main program exits
    scraping_thread.start()

    # Run the Flask app
    app.run(debug=True)