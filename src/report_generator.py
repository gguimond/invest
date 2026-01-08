"""Report generation and export functionality"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from rich.table import Table
from rich.panel import Panel
from rich.console import Console


class ReportGenerator:
    """
    Generate investment reports in various formats
    Supports: Console output, TXT, JSON, CSV
    """
    
    def __init__(self, reports_dir: str = "./reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()
    
    def create_summary_table(
        self,
        sp500_data: Dict,
        cw8_data: Dict,
        currency_data: Dict,
        m2_data: Dict,
        stoxx600_data: Optional[Dict] = None
    ) -> Table:
        """Create a summary table of all key metrics"""
        table = Table(title="📊 Market Summary", show_header=True, header_style="bold cyan")
        
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("S&P 500", style="white", width=20)
        table.add_column("MSCI World", style="white", width=20)
        if stoxx600_data:
            table.add_column("STOXX 600", style="white", width=20)
        
        # Current prices
        if stoxx600_data:
            table.add_row(
                "Current Price",
                f"${sp500_data['current_price']:.2f}",
                f"${cw8_data['current_price']:.2f}",
                f"€{stoxx600_data['current_price']:.2f}"
            )
        else:
            table.add_row(
                "Current Price",
                f"${sp500_data['current_price']:.2f}",
                f"${cw8_data['current_price']:.2f}"
            )
        
        # Dip from high
        sp500_color = "green" if sp500_data['dip_pct'] < -5 else "yellow" if sp500_data['dip_pct'] < -3 else "white"
        cw8_color = "green" if cw8_data['dip_pct'] < -5 else "yellow" if cw8_data['dip_pct'] < -3 else "white"
        
        if stoxx600_data:
            stoxx_color = "green" if stoxx600_data['dip_pct'] < -5 else "yellow" if stoxx600_data['dip_pct'] < -3 else "white"
            table.add_row(
                "Dip from High",
                f"[{sp500_color}]{sp500_data['dip_pct']:.1f}%[/{sp500_color}]",
                f"[{cw8_color}]{cw8_data['dip_pct']:.1f}%[/{cw8_color}]",
                f"[{stoxx_color}]{stoxx600_data['dip_pct']:.1f}%[/{stoxx_color}]"
            )
        else:
            table.add_row(
                "Dip from High",
                f"[{sp500_color}]{sp500_data['dip_pct']:.1f}%[/{sp500_color}]",
                f"[{cw8_color}]{cw8_data['dip_pct']:.1f}%[/{cw8_color}]"
            )
        
        # RSI
        sp500_rsi_color = "green" if sp500_data['rsi'] < 40 else "red" if sp500_data['rsi'] > 60 else "white"
        cw8_rsi_color = "green" if cw8_data['rsi'] < 40 else "red" if cw8_data['rsi'] > 60 else "white"
        
        if stoxx600_data:
            stoxx_rsi_color = "green" if stoxx600_data['rsi'] < 40 else "red" if stoxx600_data['rsi'] > 60 else "white"
            table.add_row(
                "RSI (14)",
                f"[{sp500_rsi_color}]{sp500_data['rsi']:.1f}[/{sp500_rsi_color}]",
                f"[{cw8_rsi_color}]{cw8_data['rsi']:.1f}[/{cw8_rsi_color}]",
                f"[{stoxx_rsi_color}]{stoxx600_data['rsi']:.1f}[/{stoxx_rsi_color}]"
            )
        else:
            table.add_row(
                "RSI (14)",
                f"[{sp500_rsi_color}]{sp500_data['rsi']:.1f}[/{sp500_rsi_color}]",
                f"[{cw8_rsi_color}]{cw8_data['rsi']:.1f}[/{cw8_rsi_color}]"
            )
        
        # Trend
        if stoxx600_data:
            table.add_row(
                "Trend",
                sp500_data['trend'].replace('_', ' ').title(),
                cw8_data['trend'].replace('_', ' ').title(),
                stoxx600_data['trend'].replace('_', ' ').title()
            )
        else:
            table.add_row(
                "Trend",
                sp500_data['trend'].replace('_', ' ').title(),
                cw8_data['trend'].replace('_', ' ').title()
            )
        
        # Sentiment
        sp500_sent_color = "green" if sp500_data['sentiment'] > 0.05 else "red" if sp500_data['sentiment'] < -0.05 else "white"
        cw8_sent_color = "green" if cw8_data['sentiment'] > 0.05 else "red" if cw8_data['sentiment'] < -0.05 else "white"
        
        if stoxx600_data:
            stoxx_sent_color = "green" if stoxx600_data['sentiment'] > 0.05 else "red" if stoxx600_data['sentiment'] < -0.05 else "white"
            table.add_row(
                "Sentiment",
                f"[{sp500_sent_color}]{sp500_data['sentiment']:+.3f}[/{sp500_sent_color}]",
                f"[{cw8_sent_color}]{cw8_data['sentiment']:+.3f}[/{cw8_sent_color}]",
                f"[{stoxx_sent_color}]{stoxx600_data['sentiment']:+.3f}[/{stoxx_sent_color}]"
            )
        else:
            table.add_row(
                "Sentiment",
                f"[{sp500_sent_color}]{sp500_data['sentiment']:+.3f}[/{sp500_sent_color}]",
                f"[{cw8_sent_color}]{cw8_data['sentiment']:+.3f}[/{cw8_sent_color}]"
            )
        
        # Add separator
        table.add_section()
        
        # Currency info
        if stoxx600_data:
            table.add_row(
                "💱 EUR/USD Rate",
                f"{currency_data['current_rate']:.4f}",
                "N/A (EUR-based)",
                "N/A (EUR-based)"
            )
            
            table.add_row(
                "Currency Impact",
                f"{currency_data['impact']} ({currency_data['change_pct']:+.1f}%)",
                "No impact",
                "✅ None (EUR)"
            )
        else:
            table.add_row(
                "💱 EUR/USD Rate",
                f"{currency_data['current_rate']:.4f}",
                "N/A (EUR-based)"
            )
            
            table.add_row(
                "Currency Impact",
                f"{currency_data['impact']} ({currency_data['change_pct']:+.1f}%)",
                "No impact"
            )
        
        # Add separator
        table.add_section()
        
        # M2 Money Supply - show both US and Eurozone if available
        if m2_data:
            # US M2 (for SP500 and CW8)
            if m2_data.get('us_yoy_growth') is not None:
                m2_us_color = "green" if m2_data['us_yoy_growth'] > 2 else "red" if m2_data['us_yoy_growth'] < -2 else "yellow"
                
                if stoxx600_data and m2_data.get('eurozone_yoy_growth') is not None:
                    # Show both US and Eurozone M2
                    m2_ez_color = "green" if m2_data['eurozone_yoy_growth'] > 2 else "red" if m2_data['eurozone_yoy_growth'] < -2 else "yellow"
                    table.add_row(
                        "💵 M2 Growth (YoY)",
                        f"[{m2_us_color}]{m2_data['us_yoy_growth']:+.1f}% (US)[/{m2_us_color}]",
                        f"[{m2_us_color}]{m2_data['us_yoy_growth']:+.1f}% (US)[/{m2_us_color}]",
                        f"[{m2_ez_color}]{m2_data['eurozone_yoy_growth']:+.1f}% (EUR)[/{m2_ez_color}]"
                    )
                    table.add_row(
                        "M2 Impact",
                        m2_data.get('us_favorability', 'unknown'),
                        m2_data.get('us_favorability', 'unknown'),
                        m2_data.get('eurozone_favorability', 'unknown')
                    )
                else:
                    # Only US M2
                    table.add_row(
                        "💵 M2 Growth (YoY)",
                        f"[{m2_us_color}]{m2_data['us_yoy_growth']:+.1f}%[/{m2_us_color}]",
                        f"[{m2_us_color}]{m2_data['us_yoy_growth']:+.1f}%[/{m2_us_color}]"
                    )
                    table.add_row(
                        "M2 Impact",
                        m2_data.get('us_favorability', 'unknown'),
                        m2_data.get('us_favorability', 'unknown')
                    )
            elif m2_data.get('yoy_growth') is not None:
                # Backward compatibility
                m2_color = "green" if m2_data['yoy_growth'] > 2 else "red" if m2_data['yoy_growth'] < -2 else "yellow"
                if stoxx600_data:
                    table.add_row(
                        "💵 M2 Growth (YoY)",
                        f"[{m2_color}]{m2_data['yoy_growth']:+.1f}%[/{m2_color}]",
                        f"[{m2_color}]{m2_data['yoy_growth']:+.1f}%[/{m2_color}]",
                        f"[{m2_color}]{m2_data['yoy_growth']:+.1f}%[/{m2_color}]"
                    )
                else:
                    table.add_row(
                        "💵 M2 Growth (YoY)",
                        f"[{m2_color}]{m2_data['yoy_growth']:+.1f}%[/{m2_color}]",
                        f"[{m2_color}]{m2_data['yoy_growth']:+.1f}%[/{m2_color}]"
                    )
                table.add_row(
                    "M2 Impact",
                    m2_data.get('favorability', 'unknown'),
                    m2_data.get('favorability', 'unknown')
                )
        
        return table
    
    def create_recommendation_table(
        self,
        sp500_rec: Dict,
        cw8_rec: Dict,
        comparison: Dict,
        stoxx600_rec: Optional[Dict] = None
    ) -> Table:
        """Create a table showing recommendations"""
        table = Table(title="🎯 Investment Recommendations", show_header=True, header_style="bold cyan")
        
        table.add_column("Index", style="cyan", width=15)
        table.add_column("Recommendation", width=15)
        table.add_column("Confidence", width=12)
        table.add_column("Score", width=10)
        table.add_column("Key Factors", width=40)
        
        # Determine best index from comparison
        best_index = comparison.get('best_index', 'sp500').lower()
        
        # SP500
        sp500_emoji = self._get_recommendation_emoji(sp500_rec['recommendation'].value)
        sp500_color = self._get_recommendation_color(sp500_rec['recommendation'].value)
        sp500_factors = " • ".join(sp500_rec['reasons'][:2]) if sp500_rec['reasons'] else "See details"
        sp500_label = "📈 S&P 500" + (" ⭐" if best_index == 'sp500' else "")
        
        table.add_row(
            sp500_label,
            f"[{sp500_color}]{sp500_emoji} {sp500_rec['recommendation'].value}[/{sp500_color}]",
            f"{sp500_rec['confidence']:.0%}",
            f"{sp500_rec['score']:+d}",
            sp500_factors[:40] + "..." if len(sp500_factors) > 40 else sp500_factors
        )
        
        # CW8
        cw8_emoji = self._get_recommendation_emoji(cw8_rec['recommendation'].value)
        cw8_color = self._get_recommendation_color(cw8_rec['recommendation'].value)
        cw8_factors = " • ".join(cw8_rec['reasons'][:2]) if cw8_rec['reasons'] else "See details"
        cw8_label = "🌍 MSCI World" + (" ⭐" if best_index == 'cw8' else "")
        
        table.add_row(
            cw8_label,
            f"[{cw8_color}]{cw8_emoji} {cw8_rec['recommendation'].value}[/{cw8_color}]",
            f"{cw8_rec['confidence']:.0%}",
            f"{cw8_rec['score']:+d}",
            cw8_factors[:40] + "..." if len(cw8_factors) > 40 else cw8_factors
        )
        
        # STOXX600 (if available)
        if stoxx600_rec:
            stoxx_emoji = self._get_recommendation_emoji(stoxx600_rec['recommendation'].value)
            stoxx_color = self._get_recommendation_color(stoxx600_rec['recommendation'].value)
            stoxx_factors = " • ".join(stoxx600_rec['reasons'][:2]) if stoxx600_rec['reasons'] else "See details"
            stoxx_label = "🇪🇺 STOXX 600" + (" ⭐" if best_index == 'stoxx600' else "")
            
            table.add_row(
                stoxx_label,
                f"[{stoxx_color}]{stoxx_emoji} {stoxx600_rec['recommendation'].value}[/{stoxx_color}]",
                f"{stoxx600_rec['confidence']:.0%}",
                f"{stoxx600_rec['score']:+d}",
                stoxx_factors[:40] + "..." if len(stoxx_factors) > 40 else stoxx_factors
            )
        
        # Add separator
        table.add_section()
        
        # Overall recommendation
        overall_color = self._get_overall_color(comparison['overall_recommendation'])
        score_diff_label = f"Δ {comparison.get('score_difference', 0)}" if not stoxx600_rec else ""
        table.add_row(
            "📊 OVERALL",
            f"[{overall_color}]{comparison['overall_recommendation']}[/{overall_color}]",
            "",
            score_diff_label,
            comparison['action'][:40] + "..." if len(comparison['action']) > 40 else comparison['action']
        )
        
        return table
    
    def create_risk_assessment_table(
        self,
        recession_prob: float,
        recession_level: str,
        ai_bubble_risk: float,
        ai_bubble_level: str,
        market_tone: str,
        bullish_ratio: float,
        bearish_ratio: float
    ) -> Table:
        """Create a risk assessment summary table"""
        table = Table(title="⚠️ Risk Assessment", show_header=True, header_style="bold yellow")
        
        table.add_column("Risk Factor", style="yellow", width=25)
        table.add_column("Level", width=15)
        table.add_column("Value", width=15)
        table.add_column("Impact", width=35)
        
        # Recession risk
        recession_color = "red" if recession_level == 'high' else "yellow" if recession_level == 'moderate' else "green"
        table.add_row(
            "📉 Recession Risk",
            f"[{recession_color}]{recession_level.upper()}[/{recession_color}]",
            f"{recession_prob:.1%}",
            "High caution advised" if recession_level == 'high' else "Monitor closely" if recession_level == 'moderate' else "Low concern"
        )
        
        # AI Bubble risk
        bubble_color = "red" if ai_bubble_level == 'high' else "yellow" if ai_bubble_level == 'moderate' else "green"
        table.add_row(
            "🫧 AI/Tech Bubble",
            f"[{bubble_color}]{ai_bubble_level.upper()}[/{bubble_color}]",
            f"{ai_bubble_risk:.1%}",
            "Valuation concerns" if ai_bubble_level == 'high' else "Some concerns" if ai_bubble_level == 'moderate' else "No major concerns"
        )
        
        # Market sentiment
        tone_color = "green" if market_tone == 'bullish' else "red" if market_tone == 'bearish' else "yellow"
        table.add_row(
            "📰 Market Sentiment",
            f"[{tone_color}]{market_tone.upper()}[/{tone_color}]",
            f"Bull: {bullish_ratio:.0%} / Bear: {bearish_ratio:.0%}",
            "Positive momentum" if market_tone == 'bullish' else "Negative momentum" if market_tone == 'bearish' else "Mixed signals"
        )
        
        return table
    
    def _get_recommendation_emoji(self, rec: str) -> str:
        """Get emoji for recommendation"""
        return {
            'STRONG_BUY': '🚀',
            'BUY': '✅',
            'HOLD': '⏸️',
            'AVOID': '🛑'
        }.get(rec, '❓')
    
    def _get_recommendation_color(self, rec: str) -> str:
        """Get color for recommendation"""
        return {
            'STRONG_BUY': 'bold green',
            'BUY': 'green',
            'HOLD': 'yellow',
            'AVOID': 'red'
        }.get(rec, 'white')
    
    def _get_overall_color(self, overall: str) -> str:
        """Get color for overall recommendation"""
        return {
            'INVEST': 'bold green',
            'SELECTIVE': 'yellow',
            'WAIT': 'yellow',
            'AVOID': 'red'
        }.get(overall, 'white')
    
    def export_to_txt(
        self,
        report_data: Dict,
        filename: Optional[str] = None
    ) -> Path:
        """Export report to text file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"investment_report_{timestamp}.txt"
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("INVESTMENT ADVISORY REPORT\n")
            f.write(f"Generated: {report_data['timestamp']}\n")
            f.write(f"Risk Tolerance: {report_data['risk_tolerance']}\n")
            f.write("=" * 80 + "\n\n")
            
            # Market Summary
            f.write("MARKET SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"S&P 500:      ${report_data['sp500']['current_price']:.2f} ")
            f.write(f"({report_data['sp500']['dip_pct']:+.1f}% from high)\n")
            f.write(f"MSCI World:   ${report_data['cw8']['current_price']:.2f} ")
            f.write(f"({report_data['cw8']['dip_pct']:+.1f}% from high)\n")
            
            if report_data.get('stoxx600'):
                f.write(f"STOXX 600:    €{report_data['stoxx600']['current_price']:.2f} ")
                f.write(f"({report_data['stoxx600']['dip_pct']:+.1f}% from high)\n")
            
            f.write(f"EUR/USD:      {report_data['currency']['current_rate']:.4f} ")
            f.write(f"({report_data['currency']['change_pct']:+.1f}%)\n")
            
            if report_data.get('m2'):
                if report_data['m2'].get('us_yoy_growth') is not None:
                    f.write(f"US M2 Growth:     {report_data['m2']['us_yoy_growth']:+.1f}% YoY ")
                    f.write(f"({report_data['m2'].get('us_favorability', 'unknown')})\n")
                if report_data['m2'].get('eurozone_yoy_growth') is not None:
                    f.write(f"Eurozone M2 Growth: {report_data['m2']['eurozone_yoy_growth']:+.1f}% YoY ")
                    f.write(f"({report_data['m2'].get('eurozone_favorability', 'unknown')})\n")
                elif report_data['m2'].get('yoy_growth') is not None:
                    f.write(f"M2 Growth:    {report_data['m2']['yoy_growth']:+.1f}% YoY ")
                    f.write(f"({report_data['m2'].get('favorability', 'unknown')})\n")
            
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            
            indices = [('S&P 500', 'sp500'), ('MSCI World', 'cw8')]
            if report_data.get('stoxx600'):
                indices.append(('STOXX 600', 'stoxx600'))
            
            for idx_name, idx_key in indices:
                rec = report_data['recommendations'][idx_key]
                f.write(f"\n{idx_name}:\n")
                f.write(f"  Recommendation: {rec['recommendation']}\n")
                f.write(f"  Confidence: {rec['confidence']:.0%}\n")
                f.write(f"  Score: {rec['score']:+d}/100\n")
                
                if rec.get('reasons'):
                    f.write(f"  Positive Factors:\n")
                    for reason in rec['reasons']:
                        f.write(f"    • {reason}\n")
                
                if rec.get('risk_factors'):
                    f.write(f"  Risk Factors:\n")
                    for risk in rec['risk_factors']:
                        f.write(f"    • {risk}\n")
            
            # Overall
            if report_data.get('comparison'):
                comp = report_data['comparison']
                f.write(f"\nOVERALL: {comp['overall_recommendation']}\n")
                f.write(f"{comp['action']}\n")
                f.write(f"{comp['message']}\n")
            
            # Risk Assessment
            f.write("\n")
            f.write("RISK ASSESSMENT\n")
            f.write("-" * 80 + "\n")
            f.write(f"Recession Probability: {report_data['risks']['recession_prob']:.1%} ")
            f.write(f"({report_data['risks']['recession_level']})\n")
            f.write(f"AI Bubble Risk: {report_data['risks']['ai_bubble_risk']:.1%} ")
            f.write(f"({report_data['risks']['ai_bubble_level']})\n")
            f.write(f"Market Sentiment: {report_data['risks']['market_tone']} ")
            f.write(f"(Bullish: {report_data['risks']['bullish_ratio']:.0%}, ")
            f.write(f"Bearish: {report_data['risks']['bearish_ratio']:.0%})\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("DISCLAIMER: This is not financial advice. Invest at your own risk.\n")
            f.write("=" * 80 + "\n")
        
        return filepath
    
    def export_to_json(
        self,
        report_data: Dict,
        filename: Optional[str] = None
    ) -> Path:
        """Export report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"investment_report_{timestamp}.json"
        
        filepath = self.reports_dir / filename
        
        # Convert Enum values to strings
        json_data = self._prepare_for_json(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return filepath
    
    def export_to_csv(
        self,
        report_data: Dict,
        filename: Optional[str] = None
    ) -> Path:
        """Export report summary to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"investment_report_{timestamp}.csv"
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Investment Advisory Report'])
            writer.writerow(['Timestamp', report_data['timestamp']])
            writer.writerow(['Risk Tolerance', report_data['risk_tolerance']])
            writer.writerow([])
            
            # Market data
            writer.writerow(['Index', 'Price', 'Dip %', 'RSI', 'Trend', 'Sentiment', 'Recommendation', 'Confidence', 'Score'])
            
            indices = [('S&P 500', 'sp500'), ('MSCI World', 'cw8')]
            if report_data.get('stoxx600'):
                indices.append(('STOXX 600', 'stoxx600'))
            
            for idx_name, idx_key in indices:
                idx_data = report_data[idx_key]
                rec = report_data['recommendations'][idx_key]
                
                writer.writerow([
                    idx_name,
                    f"{idx_data['current_price']:.2f}",
                    f"{idx_data['dip_pct']:.2f}",
                    f"{idx_data['rsi']:.1f}",
                    idx_data['trend'],
                    f"{idx_data['sentiment']:.3f}",
                    rec['recommendation'],
                    f"{rec['confidence']:.2%}",
                    rec['score']
                ])
            
            writer.writerow([])
            
            # Currency
            writer.writerow(['Currency Data'])
            writer.writerow(['EUR/USD Rate', report_data['currency']['current_rate']])
            writer.writerow(['Change %', report_data['currency']['change_pct']])
            writer.writerow(['Impact', report_data['currency']['impact']])
            writer.writerow([])
            
            # M2
            if report_data.get('m2'):
                writer.writerow(['M2 Money Supply'])
                if report_data['m2'].get('us_yoy_growth') is not None:
                    writer.writerow(['US M2 YoY Growth %', report_data['m2']['us_yoy_growth']])
                    writer.writerow(['US M2 Favorability', report_data['m2'].get('us_favorability', 'unknown')])
                if report_data['m2'].get('eurozone_yoy_growth') is not None:
                    writer.writerow(['Eurozone M2 YoY Growth %', report_data['m2']['eurozone_yoy_growth']])
                    writer.writerow(['Eurozone M2 Favorability', report_data['m2'].get('eurozone_favorability', 'unknown')])
                elif report_data['m2'].get('yoy_growth') is not None:
                    writer.writerow(['YoY Growth %', report_data['m2']['yoy_growth']])
                    writer.writerow(['Favorability', report_data['m2'].get('favorability', 'unknown')])
                writer.writerow([])
            
            # Risks
            writer.writerow(['Risk Assessment'])
            writer.writerow(['Recession Probability', f"{report_data['risks']['recession_prob']:.2%}"])
            writer.writerow(['AI Bubble Risk', f"{report_data['risks']['ai_bubble_risk']:.2%}"])
            writer.writerow(['Market Tone', report_data['risks']['market_tone']])
            writer.writerow([])
            
            # Overall
            if report_data.get('comparison'):
                writer.writerow(['Overall Recommendation'])
                writer.writerow(['Decision', report_data['comparison']['overall_recommendation']])
                writer.writerow(['Action', report_data['comparison']['action']])
        
        return filepath
    
    def _prepare_for_json(self, data: Dict) -> Dict:
        """Prepare data for JSON serialization (convert Enums, etc.)"""
        import copy
        json_data = copy.deepcopy(data)
        
        # Convert recommendation Enums to strings
        for idx_key in ['sp500', 'cw8']:
            if 'recommendations' in json_data and idx_key in json_data['recommendations']:
                rec = json_data['recommendations'][idx_key].get('recommendation')
                if hasattr(rec, 'value'):
                    json_data['recommendations'][idx_key]['recommendation'] = rec.value
        
        return json_data
