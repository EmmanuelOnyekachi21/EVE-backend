from django.urls import path, include

urlpatterns = [
    path('signals/', include('apps.signals.urls')),
    path('sources/', include('apps.sources.urls')),
]

