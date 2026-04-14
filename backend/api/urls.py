from django.urls import path
from api.views import predict_anomaly

urlpatterns = [
    path('predict/',predict_anomaly),
]

