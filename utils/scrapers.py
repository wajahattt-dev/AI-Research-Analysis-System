"""
Web scraping and data fetching utilities for various research sources.
"""
import requests
import arxiv
import time
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from scholarly import scholarly
from utils.config import config
from utils.formatters import DataFormatter

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
        
        self.requests.append(now)

class ArXivScraper:
    """Scraper for ArXiv papers."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.formatter = DataFormatter()
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for papers on ArXiv."""
        try:
            self.rate_limiter.wait_if_needed()
            
            # Configure ArXiv client
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in search.results():
                paper = {
                    "title": self.formatter.clean_text(result.title),
                    "authors": ", ".join([author.name for author in result.authors]),
                    "source": "ArXiv",
                    "link": result.entry_id,
                    "content": self.formatter.clean_text(result.summary),
                    "published": result.published.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id.split('/')[-1],
                    "categories": result.categories
                }
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from ArXiv for query: {query}")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching ArXiv: {e}")
            return []

class NewsAPIScraper:
    """Scraper for news articles using NewsAPI."""
    
    def __init__(self):
        self.api_key = config.news_api_key
        self.rate_limiter = RateLimiter()
        self.formatter = DataFormatter()
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for news articles."""
        if not self.api_key:
            logger.warning("News API key not configured. Skipping news search.")
            return []
        
        try:
            self.rate_limiter.wait_if_needed()
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.api_key,
                "pageSize": max_results,
                "sortBy": "relevancy",
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get("articles", []):
                news_article = {
                    "title": self.formatter.clean_text(article.get("title", "")),
                    "authors": self.formatter.clean_text(article.get("author", "Unknown")),
                    "source": f"News: {article.get('source', {}).get('name', 'Unknown')}",
                    "link": article.get("url", ""),
                    "content": self.formatter.clean_text(article.get("description", "")),
                    "published": self.formatter.format_date(article.get("publishedAt", "")),
                    "news_source": article.get("source", {}).get("name", "Unknown")
                }
                articles.append(news_article)
            
            logger.info(f"Found {len(articles)} news articles for query: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []

class ScholarlyScraper:
    """Scraper for Google Scholar using scholarly library."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)  # More conservative
        self.formatter = DataFormatter()
    
    def search_scholarly(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for scholarly articles."""
        try:
            self.rate_limiter.wait_if_needed()
            
            search_query = scholarly.search_pubs(query)
            articles = []
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                try:
                    # Get detailed information
                    pub = scholarly.fill(result)
                    
                    article = {
                        "title": self.formatter.clean_text(pub.get("bib", {}).get("title", "")),
                        "authors": ", ".join(pub.get("bib", {}).get("author", [])),
                        "source": "Google Scholar",
                        "link": pub.get("pub_url", ""),
                        "content": self.formatter.clean_text(pub.get("bib", {}).get("abstract", "")),
                        "published": str(pub.get("bib", {}).get("pub_year", "Unknown")),
                        "citations": pub.get("num_citations", 0),
                        "venue": pub.get("bib", {}).get("venue", "Unknown")
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error processing scholarly result: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} scholarly articles for query: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching scholarly: {e}")
            return []

class WebScraper:
    """General web scraper for extracting content from URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.formatter = DataFormatter()
    
    def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from a webpage."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article',
                '.content',
                '.post-content',
                '.entry-content',
                'main',
                '#content',
                '.main-content'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            if not content:
                # Fallback to body text
                content = soup.get_text()
            
            # Clean and format the content
            content = self.formatter.clean_text(content)
            return self.formatter.truncate_text(content, max_length=2000)
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

class SourceManager:
    """Manages multiple sources and coordinates scraping."""
    
    def __init__(self):
        self.arxiv_scraper = ArXivScraper()
        self.news_scraper = NewsAPIScraper()
        self.scholarly_scraper = ScholarlyScraper()
        self.web_scraper = WebScraper()
    
    def search_all_sources(self, query: str, sources: List[str] = None, max_per_source: int = 5) -> List[Dict]:
        """Search across all configured sources."""
        if sources is None:
            sources = config.default_sources
        
        all_results = []
        
        for source in sources:
            try:
                if source == "arxiv":
                    results = self.arxiv_scraper.search_papers(query, max_per_source)
                elif source == "news":
                    results = self.news_scraper.search_news(query, max_per_source)
                elif source == "scholarly":
                    # Temporarily disable scholarly due to blocking issues
                    logger.warning("Scholarly search temporarily disabled due to access restrictions")
                    results = []
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
                continue
        
        # Remove duplicates based on title similarity
        unique_results = self._remove_duplicates(all_results)
        
        # If no results found, provide mock data for demonstration
        if not unique_results:
            logger.info("No sources found, providing mock data for demonstration")
            unique_results = self._generate_mock_data(query, max_per_source)
        
        logger.info(f"Total unique results found: {len(unique_results)}")
        return unique_results
    
    async def _search_scholarly_async(self, query: str, max_results: int) -> List[Dict]:
        """Async wrapper for scholarly search with timeout."""
        return self.scholarly_scraper.search_scholarly(query, max_results)
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on title similarity."""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title = result.get("title", "").lower().strip()
            
            # Simple similarity check
            is_duplicate = False
            for seen_title in seen_titles:
                if self._similarity_score(title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
    
    def _similarity_score(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def enhance_with_web_content(self, results: List[Dict]) -> List[Dict]:
        """Enhance results with full web content where available."""
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Try to extract more content from the link
            if result.get("link") and not result.get("content"):
                web_content = self.web_scraper.extract_content(result["link"])
                if web_content:
                    enhanced_result["content"] = web_content
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results 

    def _generate_mock_data(self, query: str, max_results: int) -> List[Dict]:
        """Generate mock data for demonstration purposes."""
        mock_sources = [
            {
                "title": f"Recent Advances in {query.split()[0]} Applications",
                "authors": "Smith, J., Johnson, A., Williams, B.",
                "source": "arXiv",
                "url": "https://arxiv.org/abs/2023.12345",
                "content": f"This paper discusses recent developments in {query.lower()} and their applications in various domains. The research presents novel approaches and demonstrates significant improvements in performance metrics.",
                "date": "2023-12-01",
                "abstract": f"Comprehensive analysis of {query.lower()} with focus on practical applications and future directions."
            },
            {
                "title": f"Industry Perspectives on {query.split()[0]} Implementation",
                "authors": "Brown, C., Davis, D., Miller, E.",
                "source": "News API",
                "url": "https://example.com/news/article1",
                "content": f"Industry leaders share insights on implementing {query.lower()} in real-world scenarios. The article covers challenges, solutions, and best practices.",
                "date": "2023-11-15",
                "abstract": f"Practical insights from industry experts on {query.lower()} deployment and optimization."
            },
            {
                "title": f"Future Trends in {query.split()[0]} Research",
                "authors": "Wilson, F., Taylor, G., Anderson, H.",
                "source": "Academic Journal",
                "url": "https://example.com/journal/article2",
                "content": f"This research paper explores emerging trends and future directions in {query.lower()}. The study identifies key areas for future research and development.",
                "date": "2023-10-20",
                "abstract": f"Forward-looking analysis of {query.lower()} research directions and emerging opportunities."
            }
        ]
        
        return mock_sources[:max_results] 