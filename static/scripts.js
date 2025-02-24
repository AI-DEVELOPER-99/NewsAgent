// Infinite Scroll
let isLoading = false;
let page = 1;

setTimeout(function () {
    window.location.reload();  // Reload the entire page
}, 5000);  // 5000 milliseconds = 5 seconds

window.addEventListener('scroll', () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 10 && !isLoading) {
        loadMoreArticles();
    }
});

function loadMoreArticles() {
    isLoading = true;
    document.getElementById('loadingSpinner').classList.remove('d-none');

    // Simulate loading more articles (replace with actual API call)
    setTimeout(() => {
        fetch(`/load-more?page=${page}`)
            .then(response => response.json())
            .then(data => {
                const articlesGrid = document.getElementById('articlesGrid');
                data.articles.forEach(article => {
                    const articleCard = `
                        <div class="col-md-6 col-lg-4 mb-4 article-card">
                            <div class="card h-100 shadow-sm">
                                ${article.image ? `<img src="${article.image}" alt="${article.headline}" class="card-img-top">` : ''}
                                <div class="card-body">
                                    <h3 class="card-title">${article.headline}</h3>
                                    <p class="card-text">${article.summary}</p>
                                    <a href="${article.link}" target="_blank" class="btn btn-primary">Read more</a>
                                    <p class="text-muted mt-2 mb-0"><small>Source: ${article.source}</small></p>
                                    <p class="text-muted mb-0"><small>Broader Topic: ${article.broader_topic}</small></p>
                                    <p class="text-muted"><small>Sub-Topic: ${article.sub_topic}</small></p>
                                </div>
                            </div>
                        </div>
                    `;
                    articlesGrid.insertAdjacentHTML('beforeend', articleCard);
                });
                page++;
                isLoading = false;
                document.getElementById('loadingSpinner').classList.add('d-none');
            })
            .catch(error => {
                console.error('Error loading more articles:', error);
                isLoading = false;
                document.getElementById('loadingSpinner').classList.add('d-none');
            });
    }, 1000); // Simulate network delay
}

// Search Functionality
document.getElementById('searchInput').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const articles = document.querySelectorAll('.article-card');

    articles.forEach(article => {
        const headline = article.querySelector('.card-title').textContent.toLowerCase();
        const summary = article.querySelector('.card-text').textContent.toLowerCase();
        if (headline.includes(searchTerm) || summary.includes(searchTerm)) {
            article.style.display = 'block';
        } else {
            article.style.display = 'none';
        }
    });
});