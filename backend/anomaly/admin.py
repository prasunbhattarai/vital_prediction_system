from django.contrib import admin
from .models import AnomalyResult


@admin.register(AnomalyResult)
class AnomalyResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'cpu_usage', 'memory_usage', 'anomaly', 'detected_at']
    list_filter = ['anomaly', 'detected_at']
