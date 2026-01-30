import argparse
import sys
from pathlib import Path

# --- Path setup so we can import from src/ ---
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def get_recommendations(args):
    """Fetch and display sentiment-based recommendations."""
    print("Fetching recommendations...")
    from sentiment.main import CryptoBot

    bot = CryptoBot()
    results = bot.run_pipeline()
    
    # Apply filters based on arguments
    recommendations = results.get("recommendations", [])
    
    # Risk filter
    if args.max_risk != "Any":
        risk_order = {"Low": 0, "Medium": 1, "High": 2}
        max_risk_level = risk_order.get(args.max_risk, 2)
        recommendations = [
            r for r in recommendations if risk_order.get(r.get("risk_level", "High"), 2) <= max_risk_level
        ]

    # Confidence filter
    if args.min_confidence > 0:
        recommendations = [
            r for r in recommendations if r.get("confidence", 0.0) >= args.min_confidence
        ]
        
    # Top N filter
    recommendations = recommendations[:args.top_n]

    print(recommendations)

def detect_iceberg_orders(args):
    """Run the iceberg order detector."""
    print(f"Detecting iceberg orders for {args.symbol}...")
    from iceberg import iceberg_detector
    iceberg_detector.predict_iceberg(args.symbol)

def check_arbitrage(args):
    """Check for arbitrage opportunities."""
    print(f"Checking for arbitrage opportunities on {', '.join(args.exchanges)}...")
    # TODO: Integrate with arbitrage module
    from arbitrage import arbitrage_checker
    arbitrage_checker.main()
    
def main():
    """Main function to run the CLI."""
    parser = argparse.ArgumentParser(description="Crypto Bot CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Recommendations command
    parser_recs = subparsers.add_parser("recommendations", help="Get investment recommendations.")
    parser_recs.add_argument("--top_n", type=int, default=5, help="Number of recommendations to return.")
    parser_recs.add_argument("--max_risk", type=str, default="Any", choices=["Any", "Low", "Medium", "High"], help="Maximum risk level.")
    parser_recs.add_argument("--min_confidence", type=float, default=0.0, help="Minimum confidence level.")
    parser_recs.set_defaults(func=get_recommendations)

    # Iceberg command
    parser_iceberg = subparsers.add_parser("iceberg", help="Detect iceberg orders.")
    parser_iceberg.add_argument("--symbol", type=str, default="BTCUSDT", help="Symbol to analyze.")
    parser_iceberg.set_defaults(func=detect_iceberg_orders)

    # Arbitrage command
    parser_arbitrage = subparsers.add_parser("arbitrage", help="Check for arbitrage opportunities.")
    parser_arbitrage.add_argument("--exchanges", nargs='+', default=["binance", "kraken"], help="List of exchanges to check.")
    parser_arbitrage.set_defaults(func=check_arbitrage)

    args = parser.parse_args()

    if hasattr(args, "func"):
        if args.command == "recommendations":
            args.func(args)
        elif args.command == "iceberg":
            args.func(args)
        elif args.command == "arbitrage":
            args.func(args)
        else:
            args.func()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
