#!/usr/bin/env python3
"""
Investment Advisory CLI Application
Main entry point for the application
"""

import sys
import click
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import (
    DEFAULT_RISK_TOLERANCE, 
    REPORTS_DIR,
    HISTORICAL_YEARS
)
from src.database import Database
from src.data_collector import DataCollector
from src.technical_analyzer import TechnicalAnalyzer, assess_currency_risk
from src.economic_data import EconomicDataCollector
from src.news_collector import NewsCollector
from src.sentiment_analyzer import SentimentAnalyzer
from src.decision_engine import DecisionEngine, DecisionFactors
from src.report_generator import ReportGenerator

console = Console()


def print_banner():
    """Print application banner"""
    banner = """
[bold cyan]📊 Investment Advisory Report[/bold cyan]
[dim]Analyze market conditions for strategic investment timing[/dim]
    """
    console.print(Panel(banner, border_style="cyan"))


def initialize_database(force: bool = False):
    """Initialize database with historical data"""
    with Database() as db:
        # Check if database already exists
        if db.database_exists() and not force:
            console.print("[yellow]⚠[/yellow] Database already initialized")
            console.print("Use --force-init to reinitialize")
            return False
        
        console.print("\n[bold]Initializing Investment Advisor Database[/bold]")
        console.print("=" * 60)
        
        # Create schema
        db.initialize_schema()
        
        # Download historical data
        collector = DataCollector()
        all_data = collector.download_all_indices()
        
        if not all_data:
            console.print("[red]✗[/red] Failed to download market data")
            return False
        
        # Store data in database
        console.print("\n[bold]Storing data in database...[/bold]")
        for index_name, data in all_data.items():
            # Validate data
            is_valid, msg = collector.validate_data(data, index_name)
            if not is_valid:
                console.print(f"[red]✗[/red] Validation failed for {index_name}: {msg}")
                continue
            
            db.store_historical_prices(index_name, data)
            
            # Update metadata
            last_date = data.index[-1].strftime('%Y-%m-%d')
            db.set_metadata(f'last_update_{index_name.lower()}', last_date)
        
        # Calculate and store currency-adjusted returns
        if 'SP500' in all_data and 'EURUSD' in all_data:
            console.print("\n[bold]Calculating currency-adjusted returns...[/bold]")
            adj_returns = collector.calculate_currency_adjusted_returns(
                all_data['SP500'],
                all_data['EURUSD']
            )
            db.store_currency_adjusted_returns(adj_returns)
            console.print("[green]✓[/green] Currency-adjusted returns calculated")
        
        # Fetch and store M2 Money Supply data
        try:
            from src.economic_data import EconomicDataCollector
            econ_collector = EconomicDataCollector()
            
            console.print("\n[bold]Fetching M2 Money Supply data...[/bold]")
            m2_data = econ_collector.fetch_m2_data()
            
            if not m2_data.empty:
                db.store_economic_indicator('M2', m2_data)
                
                # Show M2 growth rate
                m2_stats = econ_collector.calculate_m2_growth_rate(m2_data)
                if m2_stats['yoy_growth']:
                    console.print(f"[green]✓[/green] M2 YoY Growth: {m2_stats['yoy_growth']:+.1f}%")
            else:
                console.print("[yellow]⚠[/yellow] M2 data not available (FRED API key may be missing)")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Could not fetch M2 data: {str(e)}")
        
        # Store initialization timestamp
        db.set_metadata('db_initialized', datetime.now().isoformat())
        db.set_metadata('db_version', '1.1')  # Updated version for M2 support
        
        console.print("\n[bold green]✓ Database initialization complete![/bold green]")
        
        # Show stats
        stats = db.get_database_stats()
        print_database_stats(stats)
        
        return True


def update_market_data():
    """Update market data with latest prices"""
    with Database() as db:
        if not db.database_exists():
            console.print("[yellow]⚠[/yellow] Database not initialized. Run with --init first.")
            return False
        
        console.print("\n[bold]🔄 Updating Market Data[/bold]")
        console.print("=" * 60)
        
        collector = DataCollector()
        updated = False
        
        for index_name in ['SP500', 'CW8', 'STOXX600', 'EURUSD']:  # Added STOXX600
            last_date = db.get_last_update_date(index_name)
            
            if not last_date:
                console.print(f"[yellow]⚠[/yellow] No data found for {index_name}")
                continue
            
            # Check if we need to update (market might be closed today)
            new_data = collector.update_index_data(index_name, last_date)
            
            if new_data is not None and not new_data.empty:
                db.store_historical_prices(index_name, new_data)
                new_last_date = new_data.index[-1].strftime('%Y-%m-%d')
                db.set_metadata(f'last_update_{index_name.lower()}', new_last_date)
                updated = True
        
        # Update M2 data
        try:
            from src.economic_data import EconomicDataCollector
            econ_collector = EconomicDataCollector()
            
            # Get last M2 date
            m2_df = db.get_economic_indicator('M2')
            if not m2_df.empty:
                last_m2_date = m2_df.index[-1].strftime('%Y-%m-%d')
                new_m2 = econ_collector.update_m2_data(last_m2_date)
                if new_m2 is not None and not new_m2.empty:
                    db.store_economic_indicator('M2', new_m2)
                    updated = True
        except Exception as e:
            console.print(f"[dim]M2 update skipped: {str(e)}[/dim]")
        
        if updated:
            # Recalculate currency-adjusted returns if we have new data
            sp500_data = db.get_historical_prices('SP500')
            eurusd_data = db.get_historical_prices('EURUSD')
            
            if not sp500_data.empty and not eurusd_data.empty:
                adj_returns = collector.calculate_currency_adjusted_returns(
                    sp500_data,
                    eurusd_data
                )
                db.store_currency_adjusted_returns(adj_returns)
        
        console.print("\n[green]✓[/green] Market data update complete")
        return True


def print_database_stats(stats: dict):
    """Print database statistics"""
    table = Table(title="Database Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Index", style="cyan")
    table.add_column("Records", justify="right")
    table.add_column("First Date", justify="center")
    table.add_column("Last Date", justify="center")
    
    for index_name in ['SP500', 'CW8', 'EURUSD']:
        index_stats = stats.get(index_name, {})
        table.add_row(
            index_name,
            str(index_stats.get('records', 0)),
            index_stats.get('first_date', 'N/A'),
            index_stats.get('last_date', 'N/A')
        )
    
    console.print("\n")
    console.print(table)
    console.print(f"\n[dim]Database size: {stats.get('db_size_mb', 0):.2f} MB[/dim]")
    console.print(f"[dim]News articles: {stats.get('news_articles', 0)}[/dim]")
    console.print(f"[dim]Recommendations: {stats.get('recommendations', 0)}[/dim]")
    
    # Show M2 Money Supply info if available
    if 'm2_records' in stats and stats['m2_records'] > 0:
        console.print(f"\n[bold cyan]💵 M2 Money Supply[/bold cyan]")
        console.print(f"[dim]Records: {stats['m2_records']}[/dim]")
        if stats.get('m2_yoy_growth') is not None:
            growth = stats['m2_yoy_growth']
            color = "green" if growth > 2 else "yellow" if growth > -2 else "red"
            console.print(f"Latest YoY Growth: [{color}]{growth:+.1f}%[/{color}]")


@click.command()
@click.option('--init', is_flag=True, help='Initialize database with historical data')
@click.option('--force-init', is_flag=True, help='Force reinitialize database')
@click.option('--stats', is_flag=True, help='Show database statistics')
@click.option('--risk', type=click.Choice(['conservative', 'moderate', 'aggressive']), 
              default=DEFAULT_RISK_TOLERANCE, help='Risk tolerance level')
@click.option('--index', type=click.Choice(['sp500', 'cw8', 'stoxx600', 'all']), 
              default='all', help='Which index to analyze')
@click.option('--verbose', is_flag=True, help='Show detailed output')
@click.option('--force-update', is_flag=True, help='Force full data refresh')
@click.option('--export-db', is_flag=True, help='Export database to CSV files')
@click.option('--export-report', type=click.Choice(['txt', 'json', 'csv', 'all']),
              help='Export report to file format(s)')
@click.option('--summary', is_flag=True, help='Show compact summary view with tables')
def main(init, force_init, stats, risk, index, verbose, force_update, export_db, export_report, summary):
    """Investment Advisory CLI - Should I invest now?"""
    
    print_banner()
    
    # Handle initialization
    if init or force_init:
        success = initialize_database(force=force_init)
        if success:
            console.print("\n[green]Ready to use![/green] Run [bold]python invest_advisor.py[/bold] to get recommendations.")
        sys.exit(0 if success else 1)
    
    # Handle stats request
    if stats:
        with Database() as db:
            if not db.database_exists():
                console.print("[red]✗[/red] Database not initialized. Run with --init first.")
                sys.exit(1)
            
            stats_data = db.get_database_stats()
            print_database_stats(stats_data)
        sys.exit(0)
    
    # Handle database export
    if export_db:
        with Database() as db:
            if not db.database_exists():
                console.print("[red]✗[/red] Database not initialized. Run with --init first.")
                sys.exit(1)
            
            console.print("\n[bold]Exporting database to CSV...[/bold]")
            db.export_to_csv()
            console.print("\n[green]✓[/green] Export complete")
        sys.exit(0)
    
    # Main analysis workflow
    with Database() as db:
        if not db.database_exists():
            console.print("[yellow]⚠[/yellow]  Database not initialized.")
            console.print("\nFirst time setup required:")
            console.print("  [bold cyan]python invest_advisor.py --init[/bold cyan]")
            console.print(f"\nThis will download {HISTORICAL_YEARS} years of historical data (~2-5 minutes)")
            sys.exit(1)
        
        # Update market data
        update_market_data()
        
        # Perform technical analysis
        console.print("\n[bold]📊 Performing Technical Analysis[/bold]")
        console.print("=" * 60)
        
        analyzer = TechnicalAnalyzer()
        econ_collector = EconomicDataCollector()
        
        # Analyze each index
        for idx in ['SP500', 'CW8', 'STOXX600']:  # Added STOXX600
            if index != 'all' and index.upper() != idx:  # Changed 'both' to 'all'
                continue
            
            # Emoji selection
            if idx == 'SP500':
                emoji = '📈'
            elif idx == 'CW8':
                emoji = '🌍'
            else:  # STOXX600
                emoji = '�🇺'
            
            console.print(f"\n[bold cyan]{emoji} {idx} Analysis[/bold cyan]")
            console.print("─" * 60)
            
            # Get data
            df = db.get_historical_prices(idx)
            if df.empty:
                console.print(f"[red]✗[/red] No data available for {idx}")
                continue
            
            # Comprehensive technical analysis
            analysis = analyzer.calculate_comprehensive_analysis(df)
            
            # Current price and basic info
            current = analysis['dip']['current_price']
            console.print(f"Current Price: [bold]${current:.2f}[/bold]")
            
            # Dip analysis
            dip = analysis['dip']
            dip_color = "green" if dip['is_major_dip'] else "yellow" if dip['is_significant_dip'] else "white"
            console.print(f"Dip from High: [{dip_color}]{dip['dip_percentage']:.2f}%[/{dip_color}] "
                         f"(${dip['recent_high']:.2f}, {dip['days_from_high']} days ago)")
            
            # Trend analysis
            trend = analysis['trend']
            trend_emoji = "📈" if "up" in trend['trend'] else "📉" if "down" in trend['trend'] else "↔️"
            console.print(f"Trend: {trend_emoji} [bold]{trend['trend'].replace('_', ' ').title()}[/bold]")
            console.print(f"  • Price vs 50-day MA: {trend['price_vs_sma50']:+.2f}%")
            console.print(f"  • Price vs 200-day MA: {trend['price_vs_sma200']:+.2f}%")
            console.print(f"  • Golden Cross: {'✓' if trend['golden_cross'] else '✗'}")
            
            # Momentum analysis
            momentum = analysis['momentum']
            rsi_emoji = "🔴" if momentum['rsi_status'] == 'overbought' else "🟢" if momentum['rsi_status'] == 'oversold' else "⚪"
            console.print(f"\nMomentum Indicators:")
            console.print(f"  • RSI (14): {rsi_emoji} {momentum['rsi']:.1f} ({momentum['rsi_status']})")
            console.print(f"  • MACD: {'🟢 Bullish' if momentum['macd_bullish'] else '🔴 Bearish'} "
                         f"(diff: {momentum['macd_diff']:.2f})")
            console.print(f"  • Stochastic: {momentum['stochastic_k']:.1f} ({momentum['stochastic_status']})")
            
            # Volatility analysis
            volatility = analysis['volatility']
            console.print(f"\nVolatility:")
            console.print(f"  • Recent Volatility: {volatility['recent_volatility']:.1f}% (annualized) - {volatility['volatility_level']}")
            console.print(f"  • Bollinger Position: {volatility['bollinger_position']:.0f}% of range")
            console.print(f"  • ATR: {volatility['atr_percentage']:.2f}% of price")
            
            # Support/Resistance
            sr = analysis['support_resistance']
            console.print(f"\nSupport/Resistance:")
            console.print(f"  • Resistance: ${sr['resistance']:.2f} ({sr['distance_to_resistance']:+.1f}%)")
            console.print(f"  • Support: ${sr['support']:.2f} ({sr['distance_to_support']:+.1f}%)")
        
        # Currency analysis (for EUR investors)
        console.print(f"\n[bold cyan]💱 EUR/USD Currency Analysis[/bold cyan]")
        console.print("─" * 60)
        eurusd_df = db.get_historical_prices('EURUSD')
        if not eurusd_df.empty:
            curr_analysis = analyzer.calculate_comprehensive_analysis(eurusd_df)
            curr_risk = assess_currency_risk(eurusd_df)
            
            current_rate = curr_analysis['dip']['current_price']
            console.print(f"Current Rate: [bold]{current_rate:.4f}[/bold] (€1 = ${current_rate:.4f})")
            console.print(f"30-day Change: {curr_risk['change_pct']:+.2f}%")
            console.print(f"Dollar Trend: {curr_risk['trend'].title()}")
            console.print(f"Currency Risk: {curr_risk['risk_level'].upper()} ({curr_risk['impact']})")
            console.print(f"RSI: {curr_analysis['momentum']['rsi']:.1f}")
            
            # Impact on EUR investors
            if curr_risk['impact'] in ['negative', 'very_negative']:
                console.print(f"\n[yellow]⚠ Warning:[/yellow] Dollar weakness reduces EUR returns on USD investments")
            elif curr_risk['impact'] == 'positive':
                console.print(f"\n[green]✓ Positive:[/green] Dollar strength enhances EUR returns on USD investments")
        
        # M2 Money Supply Analysis
        console.print(f"\n[bold cyan]💵 M2 Money Supply Analysis[/bold cyan]")
        console.print("─" * 60)
        m2_df = db.get_economic_indicator('M2')
        if not m2_df.empty:
            m2_stats = econ_collector.calculate_m2_growth_rate(m2_df)
            m2_assessment = econ_collector.assess_m2_favorability(m2_stats['yoy_growth'])
            
            if m2_stats['current_value'] is not None:
                console.print(f"Latest M2: ${m2_stats['current_value']:.0f}B")
            if m2_stats['yoy_growth'] is not None:
                console.print(f"YoY Growth: [bold]{m2_stats['yoy_growth']:+.2f}%[/bold]")
            if m2_stats['mom_growth'] is not None:
                console.print(f"MoM Growth: {m2_stats['mom_growth']:+.2f}%")
            
            # Favorability assessment
            impact_color = "green" if m2_assessment['is_favorable'] else "red" if m2_assessment['is_favorable'] == False else "yellow"
            console.print(f"\nLiquidity Assessment: [{impact_color}]{m2_assessment['impact'].upper()}[/{impact_color}]")
            console.print(f"Score: {m2_assessment['score']:+d}")
            console.print(f"Message: {m2_assessment['message']}")
        else:
            console.print("[yellow]⚠[/yellow] M2 data not available (FRED API key required)")
            console.print("Set FRED_API_KEY in .env to enable M2 analysis")
        
        # News & Sentiment Analysis
        console.print(f"\n[bold cyan]📰 News & Sentiment Analysis[/bold cyan]")
        console.print("=" * 60)
        
        news_collector = NewsCollector()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Collect news
        news_by_category = news_collector.collect_market_news()
        
        # Analyze sentiment for each category
        console.print("\n[bold]Analyzing Sentiment by Category:[/bold]")
        console.print("─" * 60)
        
        sentiment_results = {}
        
        for category, articles in news_by_category.items():
            if not articles:
                continue
            
            # Analyze sentiment
            analyzed_articles = sentiment_analyzer.analyze_articles(articles)
            aggregate = sentiment_analyzer.aggregate_sentiment(analyzed_articles)
            
            sentiment_results[category] = {
                'articles': analyzed_articles,
                'aggregate': aggregate
            }
            
            # Display category sentiment
            category_name = category.replace('_', ' ').title()
            score = aggregate['sentiment_score']
            label = aggregate['sentiment_label']
            count = aggregate['article_count']
            
            # Color based on sentiment
            if label == 'positive':
                color = 'green'
                emoji = '🟢'
            elif label == 'negative':
                color = 'red'
                emoji = '🔴'
            else:
                color = 'yellow'
                emoji = '⚪'
            
            console.print(f"  {emoji} [{color}]{category_name:20}[/{color}] "
                         f"Score: {score:+.3f} | "
                         f"Articles: {count} "
                         f"(+{aggregate['positive_count']}, -{aggregate['negative_count']})")
        
        # Overall market sentiment
        console.print(f"\n[bold]Overall Market Assessment:[/bold]")
        console.print("─" * 60)
        
        # Combine all articles
        all_articles = news_collector.get_all_articles(news_by_category)
        analyzed_all = sentiment_analyzer.analyze_articles(all_articles)
        
        overall_sentiment = sentiment_analyzer.aggregate_sentiment(analyzed_all)
        market_analysis = sentiment_analyzer.analyze_market_sentiment(analyzed_all)
        
        console.print(f"Total Articles: {overall_sentiment['article_count']}")
        console.print(f"Overall Sentiment: [bold]{overall_sentiment['sentiment_label'].upper()}[/bold] "
                     f"(score: {overall_sentiment['sentiment_score']:+.3f})")
        console.print(f"Market Tone: [bold]{market_analysis['market_sentiment'].upper()}[/bold]")
        console.print(f"  • Bullish articles: {market_analysis['bullish_count']} ({market_analysis['bullish_ratio']:.1%})")
        console.print(f"  • Bearish articles: {market_analysis['bearish_count']} ({market_analysis['bearish_ratio']:.1%})")
        
        # Recession probability
        recession_result = sentiment_analyzer.calculate_recession_probability(analyzed_all)
        risk_color = 'red' if recession_result['level'] == 'high' else 'yellow' if recession_result['level'] == 'moderate' else 'green'
        console.print(f"\n[bold]Recession Probability:[/bold] [{risk_color}]{recession_result['probability']:.1%} ({recession_result['level'].upper()})[/{risk_color}]")
        console.print(f"  • Recession mentions: {recession_result['mention_count']} articles")
        if recession_result['mention_count'] > 0:
            console.print(f"  • Recession sentiment: {recession_result['sentiment']:+.3f}")
        
        # AI bubble risk
        bubble_result = sentiment_analyzer.calculate_ai_bubble_risk(analyzed_all)
        bubble_color = 'red' if bubble_result['level'] == 'high' else 'yellow' if bubble_result['level'] == 'moderate' else 'green'
        console.print(f"\n[bold]AI/Tech Bubble Risk:[/bold] [{bubble_color}]{bubble_result['risk']:.1%} ({bubble_result['level'].upper()})[/{bubble_color}]")
        console.print(f"  • Bubble mentions: {bubble_result['mention_count']} articles")
        if bubble_result['mention_count'] > 0:
            console.print(f"  • Bubble sentiment: {bubble_result['sentiment']:+.3f}")
        
        # Store news in database
        console.print(f"\n[dim]Storing {len(analyzed_all)} articles in database...[/dim]")
        for article in analyzed_all:
            # Determine related index
            category = article.get('category', 'market_general')
            if 'sp500' in category:
                related_index = 'SP500'
            elif 'cw8' in category:
                related_index = 'CW8'
            elif 'stoxx600' in category:
                related_index = 'STOXX600'
            elif 'dollar' in category or 'eur' in category:
                related_index = 'EURUSD'
            else:
                related_index = 'GENERAL'
            
            db.store_news_article(
                title=article.get('title', ''),
                description=article.get('description', ''),
                source=article.get('source', ''),
                published_at=article.get('published_at'),
                url=article.get('url', ''),
                sentiment_score=article.get('sentiment_score', 0),
                sentiment_label=article.get('sentiment_label', 'neutral'),
                related_index=related_index
            )
        
        console.print(f"[green]✓[/green] News analysis complete")
        
        # ============================================================
        # PHASE 4: DECISION ENGINE 🎯
        # ============================================================
        console.print(f"\n[bold cyan]🎯 Phase 4: Investment Decision Engine[/bold cyan]")
        console.print("=" * 60)
        console.print(f"Risk Tolerance: [bold]{risk.upper()}[/bold]\n")
        
        decision_engine = DecisionEngine(risk_tolerance=risk)
        
        # Prepare data for decision engine
        recommendations = {}
        tech_analyses = {}  # Store for later use in reports
        
        for idx in ['SP500', 'CW8', 'STOXX600']:  # Added STOXX600
            if index != 'all' and index.upper() != idx:  # Changed 'both' to 'all'
                continue
            
            # Emoji selection
            if idx == 'SP500':
                emoji = '📈'
            elif idx == 'CW8':
                emoji = '🌍'
            else:  # STOXX600
                emoji = '�🇺'
            
            console.print(f"[bold cyan]{emoji} {idx} Investment Recommendation[/bold cyan]")
            console.print("─" * 60)
            
            # Get technical analysis
            df = db.get_historical_prices(idx)
            if df.empty:
                console.print(f"[red]✗[/red] No data for {idx}")
                continue
            
            tech_analysis = analyzer.calculate_comprehensive_analysis(df)
            tech_analyses[idx] = tech_analysis  # Store for reports
            
            # Get sentiment for this index
            category_key = 'sp500' if idx == 'SP500' else 'cw8'
            index_sentiment = sentiment_results.get(category_key, {}).get('aggregate', {})
            
            # Use overall sentiment if index-specific not available
            if not index_sentiment:
                index_sentiment = overall_sentiment
            
            # Get currency risk (for SP500)
            currency_risk = None
            currency_change = None
            currency_impact = None
            
            if idx == 'SP500' and not eurusd_df.empty:
                curr_risk = assess_currency_risk(eurusd_df)
                currency_risk = curr_risk['risk_level']
                currency_change = curr_risk['change_pct']
                currency_impact = curr_risk['impact']
            
            # Create DecisionFactors
            factors = DecisionFactors(
                # Technical factors
                dip_percentage=tech_analysis['dip']['dip_percentage'],
                rsi=tech_analysis['momentum']['rsi'],
                rsi_status=tech_analysis['momentum']['rsi_status'],
                macd_bullish=tech_analysis['momentum']['macd_bullish'],
                trend=tech_analysis['trend']['trend'],
                price_vs_ma50=tech_analysis['trend']['price_vs_sma50'],
                price_vs_ma200=tech_analysis['trend']['price_vs_sma200'],
                golden_cross=tech_analysis['trend']['golden_cross'],
                volatility_level=tech_analysis['volatility']['volatility_level'],
                
                # Sentiment factors
                overall_sentiment=index_sentiment.get('sentiment_score', 0),
                sentiment_label=index_sentiment.get('sentiment_label', 'neutral'),
                market_tone=market_analysis['market_sentiment'],
                bullish_ratio=market_analysis['bullish_ratio'],
                bearish_ratio=market_analysis['bearish_ratio'],
                
                # Risk factors
                recession_probability=recession_result['probability'],
                recession_level=recession_result['level'],
                ai_bubble_risk=bubble_result['risk'],
                ai_bubble_level=bubble_result['level'],
                
                # M2 Money Supply (KEY FACTOR!)
                m2_yoy_growth=m2_stats.get('yoy_growth') if not m2_df.empty else None,
                m2_score=m2_assessment.get('score', 0) if not m2_df.empty else 0,
                m2_favorability=m2_assessment.get('impact', 'unknown') if not m2_df.empty else 'unknown',
                
                # Currency factors
                currency_risk_level=currency_risk,
                currency_change_pct=currency_change,
                currency_impact=currency_impact
            )
            
            # Generate recommendation
            result = decision_engine.generate_recommendation(idx, factors)
            recommendations[idx] = result
            
            # Display recommendation
            rec = result['recommendation'].value
            confidence = result['confidence']
            score = result['score']
            
            # Color coding
            if rec == 'STRONG_BUY':
                rec_color = 'bold green'
                emoji = '🚀'
            elif rec == 'BUY':
                rec_color = 'green'
                emoji = '✅'
            elif rec == 'HOLD':
                rec_color = 'yellow'
                emoji = '⏸️'
            else:  # AVOID
                rec_color = 'red'
                emoji = '🛑'
            
            console.print(f"\n[{rec_color}]{emoji} RECOMMENDATION: {rec}[/{rec_color}]")
            console.print(f"Confidence: {confidence:.0%}")
            console.print(f"Decision Score: {score:+d}/100")
            
            # Show reasons
            if result['reasons']:
                console.print(f"\n[bold green]✓ Positive Factors:[/bold green]")
                for reason in result['reasons']:
                    console.print(f"  • {reason}")
            
            # Show risk factors
            if result['risk_factors']:
                console.print(f"\n[bold red]⚠ Risk Factors:[/bold red]")
                for risk in result['risk_factors']:
                    console.print(f"  • {risk}")
            
            console.print()
        
        # Comparative analysis (support 2 or 3 indices)
        if len(recommendations) >= 2:
            console.print(f"\n[bold cyan]⚖️ Comparative Analysis[/bold cyan]")
            console.print("=" * 60)
            
            # Call comparison with all available recommendations
            comparison = decision_engine.compare_recommendations(
                recommendations.get('SP500'),
                recommendations.get('CW8'),
                recommendations.get('STOXX600')  # Pass None if not analyzed
            )
            
            console.print(f"{comparison['message']}")
            console.print(f"  • S&P 500 Score: {comparison['sp500_score']:+d}")
            console.print(f"  • MSCI World Score: {comparison['cw8_score']:+d}")
            if comparison.get('stoxx600_score') is not None:
                console.print(f"  • STOXX 600 Score: {comparison['stoxx600_score']:+d}")
            console.print(f"  • Difference: {comparison['score_difference']} points")
            
            overall_color = 'bold green' if comparison['overall_recommendation'] == 'INVEST' else \
                           'yellow' if comparison['overall_recommendation'] in ['SELECTIVE', 'WAIT'] else 'red'
            
            console.print(f"\n[{overall_color}]📊 OVERALL: {comparison['overall_recommendation']}[/{overall_color}]")
            console.print(f"[{overall_color}]{comparison['action']}[/{overall_color}]")
        else:
            comparison = None
        
        # ============================================================
        # PHASE 5: ENHANCED REPORTING & EXPORT 📊
        # ============================================================
        
        # Prepare report data
        report_generator = ReportGenerator(str(REPORTS_DIR))
        
        # Get stored analyses safely
        tech_analysis_sp500 = tech_analyses.get('SP500', {})
        tech_analysis_cw8 = tech_analyses.get('CW8', {})
        sp500_sentiment = sentiment_results.get('sp500', {}).get('aggregate', overall_sentiment)
        cw8_sentiment = sentiment_results.get('cw8', {}).get('aggregate', overall_sentiment)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'risk_tolerance': risk,
            'sp500': {
                'current_price': tech_analysis_sp500.get('dip', {}).get('current_price', 0),
                'dip_pct': tech_analysis_sp500.get('dip', {}).get('dip_percentage', 0),
                'rsi': tech_analysis_sp500.get('momentum', {}).get('rsi', 0),
                'trend': tech_analysis_sp500.get('trend', {}).get('trend', 'unknown'),
                'sentiment': sp500_sentiment.get('sentiment_score', 0)
            },
            'cw8': {
                'current_price': tech_analysis_cw8.get('dip', {}).get('current_price', 0),
                'dip_pct': tech_analysis_cw8.get('dip', {}).get('dip_percentage', 0),
                'rsi': tech_analysis_cw8.get('momentum', {}).get('rsi', 0),
                'trend': tech_analysis_cw8.get('trend', {}).get('trend', 'unknown'),
                'sentiment': cw8_sentiment.get('sentiment_score', 0)
            },
            'currency': {
                'current_rate': curr_analysis['dip']['current_price'] if not eurusd_df.empty else 0,
                'change_pct': curr_risk['change_pct'] if not eurusd_df.empty else 0,
                'impact': curr_risk['impact'] if not eurusd_df.empty else 'unknown'
            },
            'm2': {
                'yoy_growth': m2_stats.get('yoy_growth') if not m2_df.empty else None,
                'favorability': m2_assessment.get('impact', 'unknown') if not m2_df.empty else 'unknown'
            },
            'recommendations': {
                'sp500': {
                    'recommendation': recommendations.get('SP500', {}).get('recommendation', 'HOLD').value if hasattr(recommendations.get('SP500', {}).get('recommendation'), 'value') else 'HOLD',
                    'confidence': recommendations.get('SP500', {}).get('confidence', 0),
                    'score': recommendations.get('SP500', {}).get('score', 0),
                    'reasons': recommendations.get('SP500', {}).get('reasons', []),
                    'risk_factors': recommendations.get('SP500', {}).get('risk_factors', [])
                },
                'cw8': {
                    'recommendation': recommendations.get('CW8', {}).get('recommendation', 'HOLD').value if hasattr(recommendations.get('CW8', {}).get('recommendation'), 'value') else 'HOLD',
                    'confidence': recommendations.get('CW8', {}).get('confidence', 0),
                    'score': recommendations.get('CW8', {}).get('score', 0),
                    'reasons': recommendations.get('CW8', {}).get('reasons', []),
                    'risk_factors': recommendations.get('CW8', {}).get('risk_factors', [])
                }
            },
            'comparison': comparison,
            'risks': {
                'recession_prob': recession_result['probability'],
                'recession_level': recession_result['level'],
                'ai_bubble_risk': bubble_result['risk'],
                'ai_bubble_level': bubble_result['level'],
                'market_tone': market_analysis['market_sentiment'],
                'bullish_ratio': market_analysis['bullish_ratio'],
                'bearish_ratio': market_analysis['bearish_ratio']
            }
        }
        
        # Store references for summary tables
        tech_analysis_sp500 = analyzer.calculate_comprehensive_analysis(db.get_historical_prices('SP500'))
        tech_analysis_cw8 = analyzer.calculate_comprehensive_analysis(db.get_historical_prices('CW8'))
        sp500_sentiment = sentiment_results.get('sp500', {}).get('aggregate', overall_sentiment)
        cw8_sentiment = sentiment_results.get('cw8', {}).get('aggregate', overall_sentiment)
        
        # Show summary tables if requested
        if summary or export_report:
            console.print("\n[bold cyan]" + "=" * 60 + "[/bold cyan]")
            console.print("[bold cyan]� EXECUTIVE SUMMARY[/bold cyan]")
            console.print("[bold cyan]" + "=" * 60 + "[/bold cyan]\n")
            
            # Market Summary Table
            summary_table = report_generator.create_summary_table(
                sp500_data={
                    'current_price': tech_analysis_sp500['dip']['current_price'],
                    'dip_pct': tech_analysis_sp500['dip']['dip_percentage'],
                    'rsi': tech_analysis_sp500['momentum']['rsi'],
                    'trend': tech_analysis_sp500['trend']['trend'],
                    'sentiment': sp500_sentiment.get('sentiment_score', 0)
                },
                cw8_data={
                    'current_price': tech_analysis_cw8['dip']['current_price'],
                    'dip_pct': tech_analysis_cw8['dip']['dip_percentage'],
                    'rsi': tech_analysis_cw8['momentum']['rsi'],
                    'trend': tech_analysis_cw8['trend']['trend'],
                    'sentiment': cw8_sentiment.get('sentiment_score', 0)
                },
                currency_data={
                    'current_rate': curr_analysis['dip']['current_price'] if not eurusd_df.empty else 0,
                    'change_pct': curr_risk['change_pct'] if not eurusd_df.empty else 0,
                    'impact': curr_risk['impact'] if not eurusd_df.empty else 'unknown'
                },
                m2_data={
                    'yoy_growth': m2_stats.get('yoy_growth') if not m2_df.empty else None,
                    'favorability': m2_assessment.get('impact', 'unknown') if not m2_df.empty else 'unknown'
                }
            )
            console.print(summary_table)
            console.print()
            
            # Recommendation Table
            if len(recommendations) == 2:
                rec_table = report_generator.create_recommendation_table(
                    recommendations['SP500'],
                    recommendations['CW8'],
                    comparison
                )
                console.print(rec_table)
                console.print()
            
            # Risk Assessment Table
            risk_table = report_generator.create_risk_assessment_table(
                recession_result['probability'],
                recession_result['level'],
                bubble_result['risk'],
                bubble_result['level'],
                market_analysis['market_sentiment'],
                market_analysis['bullish_ratio'],
                market_analysis['bearish_ratio']
            )
            console.print(risk_table)
            console.print()
        
        # Export reports if requested
        if export_report:
            console.print("\n[bold cyan]📁 Exporting Reports[/bold cyan]")
            console.print("=" * 60)
            
            exported_files = []
            
            if export_report in ['txt', 'all']:
                filepath = report_generator.export_to_txt(report_data)
                console.print(f"[green]✓[/green] TXT report: {filepath}")
                exported_files.append(filepath)
            
            if export_report in ['json', 'all']:
                filepath = report_generator.export_to_json(report_data)
                console.print(f"[green]✓[/green] JSON report: {filepath}")
                exported_files.append(filepath)
            
            if export_report in ['csv', 'all']:
                filepath = report_generator.export_to_csv(report_data)
                console.print(f"[green]✓[/green] CSV report: {filepath}")
                exported_files.append(filepath)
            
            console.print(f"\n[bold green]✓ Exported {len(exported_files)} report(s)[/bold green]")
        
        # Summary
        if not summary:
            console.print("\n[bold]�📋 Summary[/bold]")
            console.print("=" * 60)
            stats_data = db.get_database_stats()
            print_database_stats(stats_data)
        
        console.print("\n[bold green]✓ Phase 1 (Database & Data Collection) - Complete[/bold green]")
        console.print("[bold green]✓ Phase 2 (Technical Analysis + M2) - Complete[/bold green]")
        console.print("[bold green]✓ Phase 3 (News & Sentiment) - Complete[/bold green]")
        console.print("[bold green]✓ Phase 4 (Decision Engine) - Complete[/bold green]")
        console.print("[bold green]✓ Phase 5 (CLI Enhancement & Reports) - Complete[/bold green]")
        console.print("[dim]🎉 All core phases complete![/dim]")
        
        # Tips
        if not summary and not export_report:
            console.print("\n[dim]💡 Tips:[/dim]")
            console.print("[dim]  • Use --summary for compact table view[/dim]")
            console.print("[dim]  • Use --export-report txt/json/csv/all to save reports[/dim]")
            console.print("[dim]  • Use --risk conservative/moderate/aggressive to adjust thresholds[/dim]")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {str(e)}")
        if '--verbose' in sys.argv:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)
