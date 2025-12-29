from django.contrib import admin
from unfold.admin import ModelAdmin
from leaflet.admin import LeafletGeoAdmin
from .models import Country, State, City, Specialzone


class UnfoldLeafletMixin(ModelAdmin, LeafletGeoAdmin):

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


class CountryAdmin(UnfoldLeafletMixin):
    menu_icon = "globe-2"
    search_fields = ["name"]          # adjust field names as in your model


class StateAdmin(UnfoldLeafletMixin):
    menu_icon = "map"
    search_fields = ["name"]          # e.g. state name
    list_filter = ["country"]         # optional: sidebar filter by country


class CityAdmin(UnfoldLeafletMixin):
    menu_icon = "map-pin"
    search_fields = ["name"]          # city name
    list_filter = ["state"]           # optional


class SpecialzoneAdmin(UnfoldLeafletMixin):
    menu_icon = "star"
    search_fields = ["name"]          # or another field


admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Specialzone, SpecialzoneAdmin)