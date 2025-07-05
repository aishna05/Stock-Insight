from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Prediction
from .ml.predictor import predict_stock_and_generate_plots  
import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import glob
import os
from django.conf import settings
from django.shortcuts import render
from .ml.predictor import predict_stock_and_generate_plots
from django.conf import settings


class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticker = request.data.get("ticker", "").upper().strip()
        if not ticker:
            return Response({"error": "Ticker is required"}, status=400)

        try:
            price, mse, rmse, r2, plot1_path, plot2_path = predict_stock_and_generate_plots(ticker)

            # Convert absolute to relative paths for ImageField
            plot1_rel = os.path.relpath(plot1_path, settings.MEDIA_ROOT)
            plot2_rel = os.path.relpath(plot2_path, settings.MEDIA_ROOT)

            prediction = Prediction.objects.create(
                user=request.user,
                ticker=ticker,
                next_day_price=price,
                mse=mse,
                rmse=rmse,
                r2=r2,
                plot_1=plot1_rel,
                plot_2=plot2_rel
            )

            return Response({
                "next_day_price": price,
                "mse": mse,
                "rmse": rmse,
                "r2": r2,
                "plot_urls": [
                    request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_1.name),
                    request.build_absolute_uri(settings.MEDIA_URL + prediction.plot_2.name)
                ]
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class PredictionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ticker = request.query_params.get("ticker", "").upper()
        queryset = Prediction.objects.filter(user=request.user)
        if ticker:
            queryset = queryset.filter(ticker=ticker)

        results = []
        for p in queryset.order_by('-created_at'):
            results.append({
                "ticker": p.ticker,
                "next_day_price": p.next_day_price,
                "created_at": p.created_at,
                "plot_urls": [
                    request.build_absolute_uri(settings.MEDIA_URL + p.plot_1.name),
                    request.build_absolute_uri(settings.MEDIA_URL + p.plot_2.name)
                ]
            })
        return Response(results)

@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})

def dashboard(request):
    context = {
        'MEDIA_URL': settings.MEDIA_URL,  
    }

    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper().strip()
        if not ticker:
            context["error"] = "Ticker symbol is required."
        else:
            try:
                price, mse, rmse, r2, plot1_path, plot2_path = predict_stock_and_generate_plots(ticker)

                plot1_rel = os.path.relpath(plot1_path, settings.MEDIA_ROOT)
                plot2_rel = os.path.relpath(plot2_path, settings.MEDIA_ROOT)

                context.update({
                    "ticker": ticker,
                    "price": price,
                    "mse": mse,
                    "rmse": rmse,
                    "r2": r2,
                    "plot1_url": settings.MEDIA_URL + plot1_rel.replace('\\', '/'),
                    "plot2_url": settings.MEDIA_URL + plot2_rel.replace('\\', '/'),
                })

            except Exception as e:
                context["error"] = str(e)

    # Load existing plots
    import glob
    plot_files = glob.glob(os.path.join(settings.MEDIA_ROOT, 'plots', '*_plot*.png'))
    plot_urls = [settings.MEDIA_URL + os.path.relpath(path, settings.MEDIA_ROOT).replace('\\', '/') for path in plot_files]
    context["existing_plots"] = plot_urls

    return render(request, "dashboard.html", context)