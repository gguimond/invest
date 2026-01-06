"""News collection and sentiment analysis module"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote
import time
from rich.console import Console

from src.config import NEWS_LOOKBACK_DAYS

console = Console()


class NewsCollector:
    """Collect news from various free sources"""
    
    def __init__(self, lookback_days: int = None):
        self.lookback_days = lookback_days or NEWS_LOOKBACK_DAYS
        self.cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
    
    def fetch_google_news(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch news from Google News RSS feed
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news articles
        """
        articles = []
        
        try:
            # Google News RSS URL
            encoded_query = quote(query)
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            # Parse feed
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    # Parse published date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # Skip old articles
                    if pub_date and pub_date < self.cutoff_date:
                        continue
                    
                    article = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'published_at': pub_date,
                        'source': 'Google News',
                        'query': query
                    }
                    articles.append(article)
                    
                except Exception as e:
                    console.print(f"[dim]Error parsing article: {str(e)}[/dim]")
                    continue
            
            # Small delay to be respectful
            time.sleep(0.5)
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not fetch Google News for '{query}': {str(e)}")
        
        return articles
    
    def fetch_yahoo_finance_rss(self, max_results: int = 20) -> List[Dict]:
        """
        Fetch news from Yahoo Finance RSS feed
        
        Returns:
            List of news articles
        """
        articles = []
        
        try:
            url = "https://finance.yahoo.com/news/rssindex"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_results]:
                try:
                    # Parse published date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # Skip old articles
                    if pub_date and pub_date < self.cutoff_date:
                        continue
                    
                    article = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'published_at': pub_date,
                        'source': 'Yahoo Finance',
                        'query': 'general_market'
                    }
                    articles.append(article)
                    
                except Exception as e:
                    continue
            
            time.sleep(0.5)
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not fetch Yahoo Finance RSS: {str(e)}")
        
        return articles
    
    def collect_market_news(self) -> Dict[str, List[Dict]]:
        """
        Collect news for all relevant topics
        
        Returns:
            Dictionary of news by category
        """
        news_by_category = {
            'sp500': [],
            'cw8': [],
            'market_general': [],
            'recession': [],
            'ai_bubble': [],
            'fed_policy': [],
            'ecb_policy': [],
            'dollar_eur': [],
            'm2_liquidity': []
        }
        
        console.print("\n[bold]📰 Collecting News[/bold]")
        console.print("─" * 60)
        
        # S&P 500 news - INCREASED from 15 to 30
        console.print("• Fetching S&P 500 news...")
        news_by_category['sp500'] = self.fetch_google_news("S&P 500 stock market", max_results=30)
        
        # MSCI World / Global markets - INCREASED from 10 to 25
        console.print("• Fetching MSCI World news...")
        news_by_category['cw8'] = self.fetch_google_news("MSCI World index global stocks", max_results=25)
        
        # General market news - INCREASED from 15 to 30
        console.print("• Fetching general market news...")
        news_by_category['market_general'] = self.fetch_yahoo_finance_rss(max_results=30)
        
        # Recession indicators - INCREASED from 10 to 20
        console.print("• Fetching recession news...")
        news_by_category['recession'] = self.fetch_google_news("recession economy unemployment GDP", max_results=20)
        
        # AI bubble - INCREASED from 10 to 20
        console.print("• Fetching AI sector news...")
        news_by_category['ai_bubble'] = self.fetch_google_news("AI artificial intelligence bubble tech stocks valuation", max_results=20)
        
        # Fed policy - INCREASED from 10 to 20
        console.print("• Fetching Federal Reserve news...")
        news_by_category['fed_policy'] = self.fetch_google_news("Federal Reserve Fed interest rates policy", max_results=20)
        
        # ECB policy - INCREASED from 8 to 15
        console.print("• Fetching ECB news...")
        news_by_category['ecb_policy'] = self.fetch_google_news("European Central Bank ECB euro policy", max_results=15)
        
        # Dollar / EUR/USD - INCREASED from 10 to 20
        console.print("• Fetching currency news...")
        news_by_category['dollar_eur'] = self.fetch_google_news("dollar euro EUR/USD exchange rate currency", max_results=20)
        
        # M2 Money Supply / Liquidity - INCREASED from 8 to 20
        console.print("• Fetching liquidity news...")
        news_by_category['m2_liquidity'] = self.fetch_google_news("money supply liquidity M2 monetary policy", max_results=20)
        
        # Count total articles
        total = sum(len(articles) for articles in news_by_category.values())
        console.print(f"\n[green]✓[/green] Collected {total} news articles across all categories")
        
        return news_by_category
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles based on title similarity
        
        Args:
            articles: List of articles
            
        Returns:
            Deduplicated list
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Simple deduplication by title
            title_key = article['title'].lower().strip()[:50]  # First 50 chars
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_all_articles(self, news_by_category: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Get all articles combined and deduplicated
        
        Returns:
            List of all unique articles
        """
        all_articles = []
        
        for category, articles in news_by_category.items():
            for article in articles:
                article['category'] = category
                all_articles.append(article)
        
        # Deduplicate
        unique_articles = self.deduplicate_articles(all_articles)
        
        # Sort by date (newest first)
        unique_articles.sort(
            key=lambda x: x['published_at'] if x['published_at'] else datetime.min,
            reverse=True
        )
        
        return unique_articles
