from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import (
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market, CountryInfo,
    DestinationGuide, PlaceInformation, TravelHacks, Festivals, FamousPhotoPoint, Activities, Hotel
)
from social.serializers import SocialPostSerializer


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


# Detailed serializers with social posts
class DetailedPinSerializer(PinSerializer):
    """Base detailed serializer for pin models with social posts."""
    social_posts = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta(PinSerializer.Meta):
        fields = PinSerializer.Meta.fields + ['slug', 'created_by_name', 'social_posts', 'marker_icon']
    
    def get_social_posts(self, obj):
        # Get social posts related to this pin
        model_name = obj._meta.model_name
        field_mapping = {
            'mainattraction': 'mainattraction',
            'thingstodo': 'thingsToDo',
            'placestovisit': 'placestovisit',
            'placestoeat': 'placesToEat',
            'market': 'market',
            'countryinfo': 'countryinfo',
            'destinationguide': 'DestinationGuide',
            'placeinformation': 'placeinformation',
            'travelhacks': 'travelhacks',
            'festivals': 'Festivals',
            'famousphotopoint': 'famousphotopoint',
            'activities': 'activites',
            'hotel': 'hotel'
        }
        
        field_name = field_mapping.get(model_name)
        if field_name:
            from social.models import SocialPost
            filter_kwargs = {field_name: obj, 'published': True}
            posts = SocialPost.objects.filter(**filter_kwargs).select_related('platform').prefetch_related('tags')
            return SocialPostSerializer(posts, many=True).data
        return []


class DetailedMainAttractionSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = MainAttraction


class DetailedThingsToDoSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = ThingsToDo


class DetailedPlacesToVisitSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = PlacesToVisit


class DetailedPlacesToEatSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = PlacesToEat


class DetailedMarketSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = Market


class DetailedCountryInfoSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = CountryInfo


class DetailedDestinationGuideSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = DestinationGuide


class DetailedPlaceInformationSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = PlaceInformation


class DetailedTravelHacksSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = TravelHacks


class DetailedFestivalsSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = Festivals


class DetailedFamousPhotoPointSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = FamousPhotoPoint


class DetailedActivitiesSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = Activities


class DetailedHotelSerializer(DetailedPinSerializer):
    class Meta(DetailedPinSerializer.Meta):
        model = Hotel