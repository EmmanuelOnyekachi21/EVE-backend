from django.contrib.gis import admin as gis_admin
from .models import Signal


@gis_admin.register(Signal)
class SignalAdmin(gis_admin.GISModelAdmin):
    list_display = [
        'id',
        'signal_type',
        'occurred_at',
        'source_display',
        'location_display',
        'created_at',
    ]
    list_filter = [
        'signal_type',
        'source__platform',
    ]
    date_hierarchy = 'occurred_at'
    search_fields = [
        'content',
        'dedup_hash',
    ]
    readonly_fields = [
        'dedup_hash',
        'created_at',
    ]

    def location_display(self, obj):
        if obj.location:
            lat = obj.location.y
            lon = obj.location.x
            return f"{lat:.5f}, {lon:.5f}"
        return "No location"
    location_display.short_description = "Location (Lat, Lon)"

    def source_display(self, obj):
        return f"{obj.source.platform}:{obj.source.external_identifier}"
    source_display.short_description = "Source"
