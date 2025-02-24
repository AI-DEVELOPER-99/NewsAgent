import httpx
from bs4 import BeautifulSoup
from transformers import pipeline
import time
from .summarizer import fetch_article_content
import json  # Add at the top

def save_articles_to_cache():
    global articles
    with open('cached_articles.json', 'w') as f:
        json.dump(articles, f, default=str)

def load_cached_articles():
    global articles
    try:
        with open('cached_articles.json', 'r') as f:
            articles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        articles = {}
    return articles

articles = []

sites_config = [
    {
        'name': 'India Today',
        'base_url': 'https://www.indiatoday.in',
        'article_tag': 'article',
        'article_class': 'B1S3_story__card__A_fhi',
        'headline_tag': 'h2',
        'summary_tag': 'p',
        'num_pages': 10  # Number of pages to scrape for this site
    },
    {
        'name': 'Indian Express',
        'base_url': 'https://indianexpress.com/section/india/',
        'article_tag': 'div',
        'article_class': 'articles',
        'headline_tag': 'h2',
        'summary_tag': 'p',
        'num_pages': 10  # Number of pages to scrape for this site
    }
]

# Define broader topics and subcategories
broader_topics = {
    "World News": [
        "UK", "US", "Europe", "Asia", "Middle East", "Africa", "China", "Malaysia", "Pakistan", "Russia", "India", "Australia", 
        "South America", "North Korea", "United Nations", "Climate Change", "Elections", "Immigration", "Trade Wars", "Pandemics", 
        "Natural Disasters", "Terrorism", "Diplomacy", "Human Rights", "Refugees", "Global Economy", "Brexit", "NATO", "ASEAN", "G7", "G20"
    ],
    "Sports": [
        "Football", "Cricket", "Tennis", "Olympics", "Snooker", "Basketball", "Rugby", "Golf", "Athletics", "Cycling", "Formula 1", 
        "Boxing", "MMA", "Swimming", "Volleyball", "Baseball", "Hockey", "Badminton", "Table Tennis", "Esports", "Surfing", "Skiing", 
        "Snowboarding", "Marathons", "Triathlons", "Wrestling", "Extreme Sports", "Sports Betting", "Sports Science", "Sports Medicine"
    ],
    "Technology": [
        "Microsoft", "Apple", "AI", "Space", "Technology", "Meta", "Adobe", "Google", "Amazon", "Tesla", "Robotics", "Cybersecurity", 
        "Blockchain", "Quantum Computing", "5G", "IoT", "Virtual Reality", "Augmented Reality", "Cloud Computing", "Big Data", 
        "Machine Learning", "Deep Learning", "Nanotechnology", "Biotechnology", "3D Printing", "Drones", "Autonomous Vehicles", 
        "Renewable Energy Tech", "Wearable Tech", "Fintech", "Edtech", "Healthtech", "Agritech", "Smart Cities", "Open Source", 
        "Programming Languages", "Software Development", "Hardware Innovations"
    ],
    "Entertainment": [
        "Movie", "Music", "Celebrity", "Release", "TV Shows", "Streaming Services", "Awards", "Festivals", "Theater", "Gaming", "Comics", 
        "Books", "Podcasts", "Anime", "K-pop", "Bollywood", "Hollywood", "Documentaries", "Reality TV", "Stand-up Comedy", "Dance", 
        "Art", "Photography", "Fashion", "Cosplay", "Fan Theories", "Fan Fiction", "Memes", "Social Media Trends", "Viral Content", 
        "Influencers", "YouTube", "TikTok", "Netflix", "Disney+", "Spotify", "Concerts", "Music Festivals", "Film Festivals", "Broadway"
    ],
    "Science": [
        "Physics", "Chemistry", "Biology", "Astronomy", "Geology", "Environmental Science", "Neuroscience", "Psychology", "Paleontology", 
        "Genetics", "Climate Science", "Space Exploration", "Mars Missions", "Black Holes", "Quantum Physics", "Renewable Energy", 
        "Medical Research", "Vaccines", "Epidemiology", "Artificial Life", "Astrobiology", "Nanomedicine", "CRISPR", "Stem Cells", 
        "Zoology", "Botany", "Marine Biology", "Archaeology", "Anthropology"
    ],
    "Business": [
        "Startups", "Entrepreneurship", "Stock Market", "Cryptocurrency", "Venture Capital", "Mergers and Acquisitions", "E-commerce", 
        "Retail", "Supply Chain", "Marketing", "Advertising", "Branding", "Leadership", "Management", "Remote Work", "Freelancing", 
        "Corporate Social Responsibility", "Sustainability", "Global Trade", "Economic Policies", "Inflation", "Recession", "Banking", 
        "Insurance", "Real Estate", "Fintech", "Cryptocurrency Regulations", "IPO", "Small Business", "Franchising"
    ],
    "Health": [
        "Fitness", "Nutrition", "Mental Health", "Yoga", "Meditation", "Chronic Diseases", "Cancer", "Diabetes", "Heart Health", 
        "COVID-19", "Vaccines", "Public Health", "Healthcare Systems", "Telemedicine", "Alternative Medicine", "Wellness", "Aging", 
        "Sleep", "Diet Trends", "Exercise Routines", "Weight Loss", "Gut Health", "Brain Health", "Women's Health", "Men's Health", 
        "Children's Health", "Pandemic Preparedness", "Health Insurance", "Medical Breakthroughs"
    ],
    "Lifestyle": [
        "Travel", "Food", "Fashion", "Home Decor", "Gardening", "Parenting", "Relationships", "Dating", "Weddings", "Self-Improvement", 
        "Minimalism", "Sustainability", "DIY Projects", "Hobbies", "Pets", "Cooking", "Baking", "Wine", "Coffee", "Cocktails", 
        "Adventure Travel", "Luxury Travel", "Budget Travel", "Cultural Experiences", "Festivals", "Holidays", "Time Management", 
        "Productivity", "Mindfulness", "Work-Life Balance"
    ],
    "Education": [
        "Online Learning", "STEM Education", "Higher Education", "Vocational Training", "Edtech", "Language Learning", "Coding Bootcamps", 
        "Scholarships", "Study Abroad", "Early Childhood Education", "Special Education", "Teacher Training", "Curriculum Development", 
        "Educational Policies", "Literacy", "Critical Thinking", "Research Methods", "Academic Writing", "Student Life", "Career Counseling"
    ],
    "Politics": [
        "Elections", "Political Parties", "Democracy", "Authoritarianism", "Political Scandals", "Lobbying", "Public Policy", 
        "International Relations", "Human Rights", "Social Justice", "Climate Policy", "Healthcare Policy", "Education Policy", 
        "Taxation", "Defense", "Immigration Policy", "Supreme Court", "Legislation", "Political Activism", "Protests", "Civil Rights"
    ],
    "Environment": [
        "Climate Change", "Renewable Energy", "Deforestation", "Pollution", "Wildlife Conservation", "Ocean Health", "Sustainable Living", 
        "Recycling", "Carbon Footprint", "Green Technology", "Environmental Policies", "Natural Disasters", "Biodiversity", "Eco-friendly Products", 
        "Water Conservation", "Air Quality", "Soil Health", "Urban Planning", "Environmental Activism", "Circular Economy"
    ],
    "History": [
        "Ancient History", "Medieval History", "Modern History", "World Wars", "Colonialism", "Industrial Revolution", "Cold War", 
        "Renaissance", "Exploration", "Archaeology", "Historical Figures", "Civilizations", "Cultural History", "Military History", 
        "Art History", "Religious History", "Revolutionary Movements", "Historical Discoveries", "Mythology", "Historical Preservation"
    ],
    "Art and Culture": [
        "Visual Arts", "Literature", "Music", "Dance", "Theater", "Film", "Photography", "Architecture", "Sculpture", "Poetry", 
        "Cultural Festivals", "Museums", "Galleries", "Street Art", "Digital Art", "Cultural Heritage", "Folklore", "Traditional Crafts", 
        "Cultural Exchange", "Art Criticism"
    ]
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
        image = item.find('img', recursive=True)['src'] if item.find('img') else None  # Extract image URL

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
        time.sleep(1)  # Wait 1 second between requests

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
        time.sleep(10)
        print(f"Scraped and classified {len(all_articles)} articles.")

        # Wait for 10 minutes before scraping again
        time.sleep(600)

def get_articles():
    return articles

def get_broader_topics():
    return broader_topics