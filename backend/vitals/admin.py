from django.contrib import admin
from .models import Vitals


@admin.register(Vitals)
class VitalsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'current_time', 'cpu_usage', 'memory_usage', 'disk_usage']
    list_filter = ['date']
    search_fields = ['date']
