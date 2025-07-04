from django.core.management.base import BaseCommand
from predictions.ml.predictor import generate_prediction
from predictions.models import Prediction
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = "Generate predictions for a single ticker or all tickers"

    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Single ticker')
        parser.add_argument('--all', action='store_true', help='Run for all tickers in ENV var TICKERS (comma-separated)')

    def handle(self, *args, **options):
        tickers = []

        if options['ticker']:
            tickers.append(options['ticker'].upper())
        elif options['all']:
            tickers = os.getenv("TICKERS", "").split(",")
        else:
            self.stdout.write(self.style.ERROR("Please provide --ticker or --all"))
            return

        # Use admin or first user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No user found"))
            return

        for ticker in tickers:
            try:
                result = generate_prediction(ticker)
                Prediction.objects.create(
                    user=user,
                    ticker=result["ticker"],
                    metrics=result["metrics"],
                    plot1=result["plot_paths"][0],
                    plot2=result["plot_paths"][1]
                )
                self.stdout.write(self.style.SUCCESS(f"Prediction saved for {ticker}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{ticker} failed: {e}"))
