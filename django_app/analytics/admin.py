from django.contrib import admin
from .models import AnalyticsData

@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
