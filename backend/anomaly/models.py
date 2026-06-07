from django.db import models


class AnomalyResult(models.Model):
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    anomaly = models.IntegerField()
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'anomaly_results'
        ordering = ['-detected_at']

    def __str__(self):
        return f"Anomaly {self.anomaly} at {self.detected_at}"
