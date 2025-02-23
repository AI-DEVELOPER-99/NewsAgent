from flask import Flask, render_template
import threading
import time
from helpers.webscraper import automated_scraping, get_articles, get_broader_topics

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    articles = get_articles()
    broader_topics = get_broader_topics()
    return render_template('index.html', articles=articles, broader_topics=broader_topics)

# Run the Flask app
if __name__ == '__main__':
    # Start the automated scraping thread
    scraping_thread = threading.Thread(target=automated_scraping)
    scraping_thread.daemon = True  # Daemonize thread to stop it when the main program exits
    scraping_thread.start()

    # Run the Flask app
    app.run(debug=True)