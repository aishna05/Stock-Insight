from django.urls import path
from .views import PredictView, PredictionListView , dashboard

app_name ="prediction"

urlpatterns = [
    path("predict/", PredictView.as_view(), name="predict"),
    path("predictions/", PredictionListView.as_view(), name="prediction-list"),
    path("dashboard/", dashboard,name="dashboard" )
]
