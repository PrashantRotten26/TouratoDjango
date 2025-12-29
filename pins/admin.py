from django.contrib import admin
from unfold.admin import ModelAdmin
from leaflet.admin import LeafletGeoAdmin

from pins.models import MainAttraction ,ThingsToDo,PlacesToVisit,PlacesToEat,Market,CountryInfo,DestinationGuide,PlaceInformation,TravelHacks,Festivals, FamousPhotoPoint, Activities, Hotel,HotelCategory


class UnfoldLeafletMixin(ModelAdmin, LeafletGeoAdmin):
    exclude = ("slug",)

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.js",
            "pins/js/leaflet_admin_geocoder.js",
        )


admin.site.register(MainAttraction, UnfoldLeafletMixin)
admin.site.register(ThingsToDo, UnfoldLeafletMixin)
admin.site.register(PlacesToVisit, UnfoldLeafletMixin)
admin.site.register(PlacesToEat, UnfoldLeafletMixin)
admin.site.register(Market, UnfoldLeafletMixin)
admin.site.register(CountryInfo, UnfoldLeafletMixin)
admin.site.register(DestinationGuide, UnfoldLeafletMixin)
admin.site.register(PlaceInformation, UnfoldLeafletMixin)
admin.site.register(TravelHacks, UnfoldLeafletMixin)
admin.site.register(Festivals, UnfoldLeafletMixin)
admin.site.register(FamousPhotoPoint, UnfoldLeafletMixin)
admin.site.register(Activities, UnfoldLeafletMixin)
admin.site.register(Hotel, UnfoldLeafletMixin)
admin.site.register(HotelCategory, UnfoldLeafletMixin)
