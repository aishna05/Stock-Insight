from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from predictions.ml.predictor import generate_prediction
from predictions.models import Prediction
from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_date
from .serializers import PredictionSerializer
from predictions.models import Prediction

class PredictView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker = request.data.get("ticker")
        if not ticker:
            return Response({"error": "Ticker is required"}, status=400)

        try:
            result = generate_prediction(ticker.upper())
            
            # Save to DB
            prediction = Prediction.objects.create(
                user=request.user,
                ticker=result["ticker"],
                metrics=result["metrics"],
                plot1=result["plot_paths"][0],
                plot2=result["plot_paths"][1]
            )

            return Response({
                "ticker": result["ticker"],
                "next_day_price": result["next_day_price"],
                "metrics": result["metrics"],
                "plot_urls": result["plot_urls"]
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PredictionListView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = PredictionSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Prediction.objects.filter(user=user)

        ticker = self.request.query_params.get('ticker')
        date = self.request.query_params.get('date')

        if ticker:
            queryset = queryset.filter(ticker__iexact=ticker)
        if date:
            parsed_date = parse_date(date)
            if parsed_date:
                queryset = queryset.filter(created_at__date=parsed_date)

        return queryset.order_by('-created_at')
