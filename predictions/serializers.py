from rest_framework import serializers
from predictions.models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'ticker', 'created_at', 'metrics', 'plot1', 'plot2']
