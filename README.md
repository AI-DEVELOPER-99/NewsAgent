# Automated News Scraper

An automated news scraping web application built with **Flask**, **BeautifulSoup**, and **HTTPX**. The scraper fetches news articles from multiple sources, classifies them into broader topics, and presents them on a web interface.

## Features

- **Automated Web Scraping**: Collects news from various sources at regular intervals.
- **Categorization**: Classifies articles into topics such as World News, Sports, Technology, and Entertainment.
- **Flask Web Interface**: Displays the scraped news in a user-friendly manner.
- **Threaded Scraping**: Runs the scraper in a background thread to continuously fetch news.

## Technologies Used

- **Python**: Core language for scraping and backend development.
- **Flask**: Web framework to serve scraped data.
- **BeautifulSoup**: HTML parsing and web scraping.
- **HTTPX**: For making efficient HTTP requests.
- **Bootstrap**: Frontend styling for better UI/UX.

## Installation

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/automated-news-scraper.git
   cd automated-news-scraper
   ```

2. **Create and Activate Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```sh
   python app.py
   ```

5. **Access the Web Interface**
   Open your browser and visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Configuration

The scraper is configured to extract articles from the following news sources:
- **India Today**
- **BBC News**
- **Reuters**

Modify the `sites_config` list in `helpers/webscraper.py` to add or update news sources.

## File Structure
```
📂 automated-news-scraper
│-- app.py               # Flask application
│-- helpers/
│   │-- webscraper.py    # Web scraper logic
│-- templates/
│   │-- index.html       # Web interface
│-- static/
│   │-- styles.css       # (Optional) CSS styles
│-- requirements.txt     # Python dependencies
│-- README.md            # Project documentation
```

## License

This project is licensed under the **MIT License**.
