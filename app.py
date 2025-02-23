from flask import Flask, render_template, jsonify, request
import threading
from helpers.summarizer import generate_summary
from helpers.webscraper import automated_scraping, get_articles, get_broader_topics,load_cached_articles

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    articles = get_articles()
    broader_topics = get_broader_topics()

    return render_template('index.html', articles=articles, broader_topics=broader_topics)

@app.route('/summarizer', methods=['POST'])
def summarize():
    data = request.get_json()
    topic = data.get('topic')
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    classified_articles = get_articles()
    
    if topic not in classified_articles:
        return jsonify({"error": "Topic not found"}), 404
    
    content_list = []
    for sub in classified_articles[topic].values():
        for article in sub:
            content = article.get('content', '')
            if content and content != "Content unavailable":
                content_list.append(content)
    
    if not content_list:
        return jsonify({"error": "No content to summarize"}), 404
    
    combined = ' '.join(content_list)[:8000]  # Truncate to prevent token overflow
    summary = generate_summary(combined, max_length=500)
    return jsonify({"summary": summary})

# Run the Flask app
if __name__ == '__main__':
    load_cached_articles()  # Load cache before starting server

    scraping_thread = threading.Thread(target=automated_scraping)
    scraping_thread.daemon = True  # Daemonize thread to stop it when the main program exits
    scraping_thread.start()

    # Run the Flask app
    app.run(debug=True)
