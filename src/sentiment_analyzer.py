"""Sentiment analysis module using VADER"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import numpy as np


class SentimentAnalyzer:
    """Analyze sentiment of news articles and text"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Keywords for specific analyses
        self.recession_keywords = [
            'recession', 'downturn', 'contraction', 'unemployment', 
            'layoffs', 'jobless', 'economic crisis', 'depression',
            'negative growth', 'GDP decline', 'slowdown', 'weak economy'
        ]
        
        self.ai_bubble_keywords = [
            'bubble', 'overvalued', 'overvaluation', 'correction',
            'crash', 'AI hype', 'tech bubble', 'speculation',
            'unsustainable', 'peak', 'irrational exuberance'
        ]
        
        self.bullish_keywords = [
            'rally', 'surge', 'gain', 'rise', 'bull market',
            'positive', 'growth', 'expansion', 'optimistic',
            'strong economy', 'recovery', 'upturn'
        ]
        
        self.bearish_keywords = [
            'fall', 'decline', 'drop', 'bear market', 'crash',
            'plunge', 'slump', 'negative', 'pessimistic',
            'weak', 'concerns', 'fears', 'worries'
        ]
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text using VADER
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {
                'compound': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 1,
                'label': 'neutral'
            }
        
        scores = self.analyzer.polarity_scores(text)
        
        # Classify sentiment
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': label
        }
    
    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze sentiment of a news article
        
        Args:
            article: Article dictionary with title and description
            
        Returns:
            Article with sentiment added
        """
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        sentiment = self.analyze_text(text)
        
        # Add sentiment to article
        article['sentiment_score'] = sentiment['compound']
        article['sentiment_label'] = sentiment['label']
        article['sentiment_positive'] = sentiment['positive']
        article['sentiment_negative'] = sentiment['negative']
        
        return article
    
    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Analyze sentiment for multiple articles
        
        Returns:
            Articles with sentiment added
        """
        return [self.analyze_article(article) for article in articles]
    
    def aggregate_sentiment(self, articles: List[Dict], 
                          decay_factor: float = 0.9) -> Dict:
        """
        Calculate weighted aggregate sentiment (recent news weighted more)
        
        Args:
            articles: List of articles with sentiment
            decay_factor: Weight decay for older news (0-1)
            
        Returns:
            Dictionary with aggregate sentiment metrics
        """
        if not articles:
            return {
                'sentiment_score': 0,
                'sentiment_label': 'neutral',
                'article_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        # Sort by date
        sorted_articles = sorted(
            articles,
            key=lambda x: x.get('published_at') or datetime.min,
            reverse=False  # Oldest first for decay calculation
        )
        
        weighted_sum = 0
        total_weight = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        now = datetime.now()
        
        for article in sorted_articles:
            sentiment_score = article.get('sentiment_score', 0)
            sentiment_label = article.get('sentiment_label', 'neutral')
            
            # Count by label
            if sentiment_label == 'positive':
                positive_count += 1
            elif sentiment_label == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
            
            # Calculate weight based on age
            pub_date = article.get('published_at')
            if pub_date:
                age_days = (now - pub_date).days
                weight = decay_factor ** age_days
            else:
                weight = 0.5  # Default weight for articles without date
            
            weighted_sum += sentiment_score * weight
            total_weight += weight
        
        # Calculate aggregate
        if total_weight > 0:
            aggregate_score = weighted_sum / total_weight
        else:
            aggregate_score = 0
        
        # Classify aggregate sentiment
        if aggregate_score >= 0.05:
            aggregate_label = 'positive'
        elif aggregate_score <= -0.05:
            aggregate_label = 'negative'
        else:
            aggregate_label = 'neutral'
        
        return {
            'sentiment_score': aggregate_score,
            'sentiment_label': aggregate_label,
            'article_count': len(articles),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_count / len(articles) if articles else 0,
            'negative_ratio': negative_count / len(articles) if articles else 0
        }
    
    def calculate_recession_probability(self, articles: List[Dict]) -> Dict:
        """
        Estimate recession probability based on news sentiment and keywords
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with recession probability and details
        """
        if not articles:
            return {
                'probability': 0,
                'level': 'low',
                'mention_count': 0,
                'sentiment': 0
            }
        
        recession_mentions = 0
        recession_sentiment_sum = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            # Check for recession keywords
            for keyword in self.recession_keywords:
                if keyword in text:
                    recession_mentions += 1
                    recession_sentiment_sum += article.get('sentiment_score', 0)
                    break  # Count article only once
        
        # Calculate probability based on mentions and sentiment
        mention_ratio = recession_mentions / len(articles) if articles else 0
        
        # Base probability from mention frequency
        probability = min(mention_ratio * 100, 80)  # Cap at 80%
        
        # Adjust based on sentiment
        if recession_mentions > 0:
            avg_sentiment = recession_sentiment_sum / recession_mentions
            # More negative sentiment = higher recession probability
            if avg_sentiment < -0.2:
                probability += 15
            elif avg_sentiment < 0:
                probability += 10
        
        probability = min(probability, 90)  # Cap at 90%
        
        # Classify level
        if probability > 60:
            level = 'high'
        elif probability > 30:
            level = 'moderate'
        else:
            level = 'low'
        
        return {
            'probability': probability / 100,  # Return as 0-1
            'level': level,
            'mention_count': recession_mentions,
            'sentiment': recession_sentiment_sum / recession_mentions if recession_mentions > 0 else 0
        }
    
    def calculate_ai_bubble_risk(self, articles: List[Dict]) -> Dict:
        """
        Estimate AI/tech bubble risk based on news
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with bubble risk assessment
        """
        if not articles:
            return {
                'risk': 0,
                'level': 'low',
                'mention_count': 0,
                'sentiment': 0
            }
        
        bubble_mentions = 0
        bubble_sentiment_sum = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            # Check for AI bubble keywords
            for keyword in self.ai_bubble_keywords:
                if keyword in text and ('ai' in text or 'tech' in text or 'technology' in text):
                    bubble_mentions += 1
                    bubble_sentiment_sum += article.get('sentiment_score', 0)
                    break
        
        # Calculate risk
        mention_ratio = bubble_mentions / len(articles) if articles else 0
        risk = min(mention_ratio * 100, 80)
        
        # Adjust based on sentiment
        if bubble_mentions > 0:
            avg_sentiment = bubble_sentiment_sum / bubble_mentions
            # More negative sentiment about tech = higher bubble risk
            if avg_sentiment < -0.2:
                risk += 15
            elif avg_sentiment < 0:
                risk += 10
        
        risk = min(risk, 90)
        
        # Classify level
        if risk > 60:
            level = 'high'
        elif risk > 40:
            level = 'moderate'
        else:
            level = 'low'
        
        return {
            'risk': risk / 100,
            'level': level,
            'mention_count': bubble_mentions,
            'sentiment': bubble_sentiment_sum / bubble_mentions if bubble_mentions > 0 else 0
        }
    
    def analyze_market_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Comprehensive market sentiment analysis
        
        Args:
            articles: List of articles
            
        Returns:
            Dictionary with various sentiment metrics
        """
        bullish_count = 0
        bearish_count = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            # Check for bullish keywords
            for keyword in self.bullish_keywords:
                if keyword in text:
                    bullish_count += 1
                    break
            
            # Check for bearish keywords
            for keyword in self.bearish_keywords:
                if keyword in text:
                    bearish_count += 1
                    break
        
        total = len(articles)
        bullish_ratio = bullish_count / total if total > 0 else 0
        bearish_ratio = bearish_count / total if total > 0 else 0
        
        # Determine overall market sentiment
        if bullish_ratio > bearish_ratio + 0.15:
            market_sentiment = 'bullish'
        elif bearish_ratio > bullish_ratio + 0.15:
            market_sentiment = 'bearish'
        else:
            market_sentiment = 'neutral'
        
        return {
            'market_sentiment': market_sentiment,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'bullish_ratio': bullish_ratio,
            'bearish_ratio': bearish_ratio
        }
