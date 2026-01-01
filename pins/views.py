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
    FestivalsSerializer, FamousPhotoPointSerializer, ActivitiesSerializer, HotelSerializer
)

# Model mapping dictionary
MODEL_MAPPING = {
    'things-to-do': (ThingsToDo, ThingsToDoSerializer),
    'main-attractions': (MainAttraction, MainAttractionSerializer),
    'places-to-visit': (PlacesToVisit, PlacesToVisitSerializer),
    'places-to-eat': (PlacesToEat, PlacesToEatSerializer),
    'markets': (Market, MarketSerializer),
    'country-info': (CountryInfo, CountryInfoSerializer),
    'destination-guides': (DestinationGuide, DestinationGuideSerializer),
    'place-information': (PlaceInformation, PlaceInformationSerializer),
    'travel-hacks': (TravelHacks, TravelHacksSerializer),
    'festivals': (Festivals, FestivalsSerializer),
    'famous-photo-points': (FamousPhotoPoint, FamousPhotoPointSerializer),
    'activities': (Activities, ActivitiesSerializer),
    'hotels': (Hotel, HotelSerializer),
}



@api_view(['GET'])
def all_pins(request):
    """API endpoint to get all pins from all models."""
    
    # Get all published pins from each model
    main_attractions = MainAttraction.objects.filter(published=True).select_related('city').prefetch_related('tags')
    things_to_do = ThingsToDo.objects.filter(published=True).select_related('city').prefetch_related('tags')
    places_to_visit = PlacesToVisit.objects.filter(published=True).select_related('city').prefetch_related('tags')
    places_to_eat = PlacesToEat.objects.filter(published=True).select_related('city').prefetch_related('tags')
    markets = Market.objects.filter(published=True).select_related('city').prefetch_related('tags')
    country_info = CountryInfo.objects.filter(published=True).select_related('city').prefetch_related('tags')
    destination_guides = DestinationGuide.objects.filter(published=True).select_related('city').prefetch_related('tags')
    place_information = PlaceInformation.objects.filter(published=True).select_related('city').prefetch_related('tags')
    travel_hacks = TravelHacks.objects.filter(published=True).select_related('city').prefetch_related('tags')
    festivals = Festivals.objects.filter(published=True).select_related('city').prefetch_related('tags')
    famous_photo_points = FamousPhotoPoint.objects.filter(published=True).select_related('city').prefetch_related('tags')
    activities = Activities.objects.filter(published=True).select_related('city').prefetch_related('tags')
    hotels = Hotel.objects.filter(published=True).select_related('city').prefetch_related('tags')
    
    # Serialize each queryset
    serialized_data = []
    
    serialized_data.extend(MainAttractionSerializer(main_attractions, many=True).data)
    serialized_data.extend(ThingsToDoSerializer(things_to_do, many=True).data)
    serialized_data.extend(PlacesToVisitSerializer(places_to_visit, many=True).data)
    serialized_data.extend(PlacesToEatSerializer(places_to_eat, many=True).data)
    serialized_data.extend(MarketSerializer(markets, many=True).data)
    serialized_data.extend(CountryInfoSerializer(country_info, many=True).data)
    serialized_data.extend(DestinationGuideSerializer(destination_guides, many=True).data)
    serialized_data.extend(PlaceInformationSerializer(place_information, many=True).data)
    serialized_data.extend(TravelHacksSerializer(travel_hacks, many=True).data)
    serialized_data.extend(FestivalsSerializer(festivals, many=True).data)
    serialized_data.extend(FamousPhotoPointSerializer(famous_photo_points, many=True).data)
    serialized_data.extend(ActivitiesSerializer(activities, many=True).data)
    serialized_data.extend(HotelSerializer(hotels, many=True).data)
    
    # Sort by rating (highest first)
    serialized_data.sort(key=lambda x: x['rating'] or 0, reverse=True)
    
    return Response({
        'pins': serialized_data,
        'total_count': len(serialized_data)
    })


@api_view(['GET'])
def get_pins_by_type(request, table_name):
    """API endpoint to get pins from a specific model based on table name."""
    
    if table_name not in MODEL_MAPPING:
        return Response({
            'error': 'Invalid table name',
            'available_tables': list(MODEL_MAPPING.keys())
        }, status=400)
    
    model_class, serializer_class = MODEL_MAPPING[table_name]
    pins = model_class.objects.filter(published=True).select_related('city').prefetch_related('tags')
    serialized_data = serializer_class(pins, many=True).data
    
    # Sort by rating (highest first)
    serialized_data.sort(key=lambda x: x['rating'] or 0, reverse=True)
    
    return Response({
        'pins': serialized_data,
        'total_count': len(serialized_data),
        'table_name': table_name
    })



@api_view(['GET'])
def get_pin_by_slug(request, slug):
    """
    Fetch a single pin using its slug.
    Example slug: things-to-do-red-fort-323cd
    """

    model_class = None
    serializer_class = None
    table_key = None

    # 🔥 SAFE prefix matching
    for key, (model, serializer) in MODEL_MAPPING.items():
        if slug.startswith(key + "-"):
            table_key = key
            model_class = model
            serializer_class = serializer
            break

    if not model_class:
        return Response(
            {"error": "Invalid slug or unsupported pin type"},
            status=400
        )

    pin = get_object_or_404(
        model_class,
        slug=slug,
        published=True
    )

    serializer = serializer_class(pin)

    return Response({
        "pin": serializer.data,
        "type": table_key
    })
