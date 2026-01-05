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
        
        # Store initialization timestamp
        db.set_metadata('db_initialized', datetime.now().isoformat())
        db.set_metadata('db_version', '1.0')
        
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
        
        for index_name in ['SP500', 'CW8', 'EURUSD']:
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


@click.command()
@click.option('--init', is_flag=True, help='Initialize database with historical data')
@click.option('--force-init', is_flag=True, help='Force reinitialize database')
@click.option('--stats', is_flag=True, help='Show database statistics')
@click.option('--risk', type=click.Choice(['conservative', 'moderate', 'aggressive']), 
              default=DEFAULT_RISK_TOLERANCE, help='Risk tolerance level')
@click.option('--index', type=click.Choice(['sp500', 'cw8', 'both']), 
              default='both', help='Which index to analyze')
@click.option('--verbose', is_flag=True, help='Show detailed output')
@click.option('--force-update', is_flag=True, help='Force full data refresh')
@click.option('--export-db', is_flag=True, help='Export database to CSV files')
def main(init, force_init, stats, risk, index, verbose, force_update, export_db):
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
        
        # TODO: Phase 2-4 implementation
        console.print("\n[yellow]ℹ[/yellow]  Analysis features coming in next phases:")
        console.print("  • Technical analysis (RSI, moving averages, etc.)")
        console.print("  • News sentiment analysis")
        console.print("  • Investment recommendations")
        console.print("  • Currency impact analysis")
        
        # For now, show what data we have
        stats_data = db.get_database_stats()
        print_database_stats(stats_data)
        
        console.print("\n[dim]Phase 1 (Database & Data Collection) - Complete ✓[/dim]")
        console.print("[dim]Phase 2 (Technical Analysis) - Coming soon[/dim]")


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
