from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market, CountryInfo,
    DestinationGuide, PlaceInformation, TravelHacks, Festivals, FamousPhotoPoint, Activities, Hotel
)


class PinSerializer(serializers.ModelSerializer):
    """Base serializer for all pin models."""
    city_name = serializers.CharField(source='city.name', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        fields = [
            'id', 'name', 'type', 'city_name', 'latitude', 'longitude',
            'description', 'header_image', 'icon', 'rating', 'link', 'tags'
        ]
    
    def get_latitude(self, obj):
        return obj.pin.y if obj.pin else None
    
    def get_longitude(self, obj):
        return obj.pin.x if obj.pin else None
    
    def get_type(self, obj):
        return obj._meta.model_name
    
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class MainAttractionSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = MainAttraction


class ThingsToDoSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = ThingsToDo


class PlacesToVisitSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = PlacesToVisit


class PlacesToEatSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = PlacesToEat


class MarketSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = Market


class CountryInfoSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = CountryInfo


class DestinationGuideSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = DestinationGuide


class PlaceInformationSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = PlaceInformation


class TravelHacksSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = TravelHacks


class FestivalsSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = Festivals


class FamousPhotoPointSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = FamousPhotoPoint


class ActivitiesSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = Activities


class HotelSerializer(PinSerializer):
    class Meta(PinSerializer.Meta):
        model = Hotel