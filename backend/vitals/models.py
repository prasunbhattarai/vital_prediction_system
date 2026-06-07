from django.db import models


class Vitals(models.Model):
    date = models.DateField()
    current_time = models.TimeField()
    cpu_usage = models.FloatField(null=True, blank=True)
    cpu_freq = models.FloatField(null=True, blank=True)
    cpu_switches = models.BigIntegerField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    memory_swap = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    read_write = models.FloatField(null=True, blank=True)
    net = models.FloatField(null=True, blank=True)
    bytes_sent = models.FloatField(null=True, blank=True)
    bytes_recv = models.FloatField(null=True, blank=True)
    battery_percent = models.FloatField(null=True, blank=True)
    power_plugged = models.BooleanField(null=True, blank=True)
    gpu_usage = models.FloatField(null=True, blank=True)
    gpu_temp = models.FloatField(null=True, blank=True)
    top5_processes_cpu_average = models.FloatField(null=True, blank=True)
    top5_processes_cpu_std = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vitals'
        ordering = ['-id']

    def __str__(self):
        return f"Vitals {self.date} {self.current_time}"
