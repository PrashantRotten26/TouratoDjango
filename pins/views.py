from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market, CountryInfo,
    DestinationGuide, PlaceInformation, TravelHacks, Festivals, FamousPhotoPoint, Activities, Hotel
)
from .serializers import (
    MainAttractionSerializer, ThingsToDoSerializer, PlacesToVisitSerializer,
    PlacesToEatSerializer, MarketSerializer, CountryInfoSerializer,
    DestinationGuideSerializer, PlaceInformationSerializer, TravelHacksSerializer,
    FestivalsSerializer, FamousPhotoPointSerializer, ActivitiesSerializer, HotelSerializer,
    DetailedMainAttractionSerializer, DetailedThingsToDoSerializer, DetailedPlacesToVisitSerializer,
    DetailedPlacesToEatSerializer, DetailedMarketSerializer, DetailedCountryInfoSerializer,
    DetailedDestinationGuideSerializer, DetailedPlaceInformationSerializer, DetailedTravelHacksSerializer,
    DetailedFestivalsSerializer, DetailedFamousPhotoPointSerializer, DetailedActivitiesSerializer, DetailedHotelSerializer
)

import requests
from django.http import HttpResponse
from urllib.parse import urljoin
from django.conf import settings


def geocode_nominatim_proxy(request, subpath=''):
    """Proxy endpoint to call Nominatim server from backend to avoid CORS and
    to set a proper User-Agent header as required by the Nominatim usage policy.
    It forwards query params and returns the remote response transparently.
    """
    target_base = 'https://nominatim.openstreetmap.org/'
    # Rebuild target URL from path suffix (e.g. 'search')
    target_url = urljoin(target_base, subpath)

    try:
        # Forward query params and add an email contact if not provided (Nominatim policy)
        params = request.GET.dict()
        nominatim_email = getattr(settings, 'NOMINATIM_EMAIL', None) or params.get('email')
        if nominatim_email and 'email' not in params:
            params['email'] = nominatim_email

        # Build headers: MUST include a descriptive User-Agent per Nominatim policy.
        user_agent = getattr(settings, 'NOMINATIM_USER_AGENT', None) or 'unfotour-geocoder/1.0 (contact: admin@example.com)'
        headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json',
        }

        # Forward some client headers that might be useful (language, referer)
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            headers['Accept-Language'] = request.META['HTTP_ACCEPT_LANGUAGE']
        # Set a Referer to your site if available
        try:
            headers['Referer'] = request.build_absolute_uri('/')
        except Exception:
            pass

        # Forward client's IP in X-Forwarded-For
        client_ip = request.META.get('REMOTE_ADDR')
        if client_ip:
            headers['X-Forwarded-For'] = client_ip

        resp = requests.get(target_url, params=params, headers=headers, timeout=10)
    except requests.RequestException as e:
        return HttpResponse(status=502, content=str(e))

    content_type = resp.headers.get('Content-Type', 'application/json')
    # If Nominatim returned a 4xx/5xx, include the remote body to help debugging
    if resp.status_code >= 400:
        return HttpResponse(resp.content, status=resp.status_code, content_type=content_type)

    return HttpResponse(resp.content, status=resp.status_code, content_type=content_type)

# Model mapping dictionary with both list and detail serializers
MODEL_MAPPING = {
    'main-attractions': {
        'model': MainAttraction,
        'list_serializer': MainAttractionSerializer,
        'detail_serializer': DetailedMainAttractionSerializer
    },
    'things-to-do': {
        'model': ThingsToDo,
        'list_serializer': ThingsToDoSerializer,
        'detail_serializer': DetailedThingsToDoSerializer
    },
    'places-to-visit': {
        'model': PlacesToVisit,
        'list_serializer': PlacesToVisitSerializer,
        'detail_serializer': DetailedPlacesToVisitSerializer
    },
    'places-to-eat': {
        'model': PlacesToEat,
        'list_serializer': PlacesToEatSerializer,
        'detail_serializer': DetailedPlacesToEatSerializer
    },
    'markets': {
        'model': Market,
        'list_serializer': MarketSerializer,
        'detail_serializer': DetailedMarketSerializer
    },
    'country-info': {
        'model': CountryInfo,
        'list_serializer': CountryInfoSerializer,
        'detail_serializer': DetailedCountryInfoSerializer
    },
    'destination-guides': {
        'model': DestinationGuide,
        'list_serializer': DestinationGuideSerializer,
        'detail_serializer': DetailedDestinationGuideSerializer
    },
    'place-information': {
        'model': PlaceInformation,
        'list_serializer': PlaceInformationSerializer,
        'detail_serializer': DetailedPlaceInformationSerializer
    },
    'travel-hacks': {
        'model': TravelHacks,
        'list_serializer': TravelHacksSerializer,
        'detail_serializer': DetailedTravelHacksSerializer
    },
    'festivals': {
        'model': Festivals,
        'list_serializer': FestivalsSerializer,
        'detail_serializer': DetailedFestivalsSerializer
    },
    'famous-photo-points': {
        'model': FamousPhotoPoint,
        'list_serializer': FamousPhotoPointSerializer,
        'detail_serializer': DetailedFamousPhotoPointSerializer
    },
    'activities': {
        'model': Activities,
        'list_serializer': ActivitiesSerializer,
        'detail_serializer': DetailedActivitiesSerializer
    },
    'hotels': {
        'model': Hotel,
        'list_serializer': HotelSerializer,
        'detail_serializer': DetailedHotelSerializer
    },
}


@api_view(['GET'])
def search_pins(request):
    """Search pins by name across all models."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'error': 'Query parameter q is required'}, status=400)
    
    from django.db.models import Q
    search_filter = Q(name__icontains=query)
    base_filter = {'published': True}
    
    results = []
    
    # Search across all models
    for key, config in MODEL_MAPPING.items():
        model = config['model']
        serializer = config['list_serializer']
        
        pins = model.objects.filter(search_filter, **base_filter).select_related('city').prefetch_related('tags')[:10]
        serialized = serializer(pins, many=True).data
        
        for pin in serialized:
            pin['category'] = key
        
        results.extend(serialized)
    
    # Sort by rating
    results.sort(key=lambda x: float(x['rating']) if x['rating'] else 0, reverse=True)
    
    return Response({
        'query': query,
        'results': results[:20],  # Limit to top 20
        'total_found': len(results)
    })


@api_view(['GET'])
def get_pin_by_slug(request, slug):
    """Get pin details by slug with social posts and CTA buttons."""
    
    # Map slug prefixes to MODEL_MAPPING keys
    slug_to_key_mapping = {
        'mainattraction': 'main-attractions',
        'thingstodo': 'things-to-do', 
        'placestovisit': 'places-to-visit',
        'placestoeat': 'places-to-eat',
        'market': 'markets',
        'countryinfo': 'country-info',
        'destinationguide': 'destination-guides',
        'placeinformation': 'place-information',
        'travelhacks': 'travel-hacks',
        'festivals': 'festivals',
        'famousphotopoint': 'famous-photo-points',
        'activities': 'activities',
        'hotel': 'hotels'
    }
    
    # Find matching model by slug prefix
    model_config = None
    model_key = None
    
    for slug_prefix, key in slug_to_key_mapping.items():
        if slug.startswith(slug_prefix + '-'):
            model_config = MODEL_MAPPING[key]
            model_key = key
            break
    
    if not model_config:
        return Response({'error': 'Invalid slug or unsupported pin type'}, status=400)
    
    # Get pin by slug
    try:
        pin = model_config['model'].objects.get(slug=slug, published=True)
    except model_config['model'].DoesNotExist:
        return Response({'error': 'Pin not found'}, status=404)
    
    # Use detailed serializer
    serializer = model_config['detail_serializer'](pin)
    pin_data = serializer.data
    
    # Add CTA buttons
    cta_buttons = []
    
    if pin.link:
        cta_buttons.append({
            'type': 'external_link',
            'label': 'Visit Website',
            'url': pin.link,
            'icon': 'external-link'
        })
    
    # Add booking button for hotels
    if model_key == 'hotels':
        cta_buttons.append({
            'type': 'booking',
            'label': 'Book Now',
            'url': pin.link or f'https://booking.com/search?q={pin.name}',
            'icon': 'calendar'
        })
    
    # Add directions button
    if pin.pin:
        cta_buttons.append({
            'type': 'directions',
            'label': 'Get Directions',
            'url': f'https://maps.google.com/?q={pin.pin.y},{pin.pin.x}',
            'icon': 'navigation'
        })
    
    return Response({
        'pin': pin_data,
        'category': model_key,
        'cta_buttons': cta_buttons
    })