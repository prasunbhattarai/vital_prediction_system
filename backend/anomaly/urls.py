from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_anomaly, name='anomaly-predict'),
    path('history/', views.anomaly_history, name='anomaly-history'),
]
