from django.urls import path
from .views import search_pins, get_pin_by_slug, geocode_nominatim_proxy

urlpatterns = [
    path('api/search/', search_pins, name='search_pins'),
    path('api/pin/<slug:slug>/', get_pin_by_slug, name='pin_by_slug'),
    # Proxy for Nominatim geocoding to avoid browser CORS issues
    path('geocode/nominatim/', geocode_nominatim_proxy, name='geocode_nominatim_root'),
    path('geocode/nominatim/<path:subpath>', geocode_nominatim_proxy, name='geocode_nominatim'),
]

