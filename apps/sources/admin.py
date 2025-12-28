from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Source, SourceTrustHistory


# Custom filter for trust_tier
class TrustTierFilter(SimpleListFilter):
    title = 'trust tier'
    parameter_name = 'trust_tier'

    def lookups(self, request, model_admin):
        return [
            ('low', 'Low (<40)'),
            ('medium', 'Medium (40-69)'),
            ('high', 'High (≥70)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(trust_score__lt=40)
        elif self.value() == 'medium':
            return queryset.filter(trust_score__gte=40, trust_score__lt=70)
        elif self.value() == 'high':
            return queryset.filter(trust_score__gte=70)
        return queryset


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = [
        'platform',
        'external_identifier',
        'trust_score',
        'trust_tier',
        'verified',
        'active',
        'last_fetched_at'
    ]
    readonly_fields = [
        'trust_tier',
        'created_at',
        'updated_at'
    ]
    list_filter = [
        'platform',
        'verified',
        'active',
        TrustTierFilter,
    ]
    search_fields = [
        'external_identifier'
    ]


@admin.register(SourceTrustHistory)
class SourceTrustHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'source_display',
        'trust_score',
        'changed_by',
        'valid_from',
        'valid_to',
    ]
    list_filter = [
        'changed_by',
    ]
    date_hierarchy = 'valid_from'
    search_fields = [
        'source__external_identifier',
        'source__platform',
    ]
    readonly_fields = [
        'valid_from',
    ]

    def source_display(self, obj):
        return f"{obj.source.platform}:{obj.source.external_identifier}"
    source_display.short_description = "Source"
    
