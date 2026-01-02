from django.contrib import admin
from unfold.admin import ModelAdmin
from leaflet.admin import LeafletGeoAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from taggit.models import TaggedItem



from pins.models import MainAttraction ,ThingsToDo,PlacesToVisit,PlacesToEat,Market,CountryInfo,DestinationGuide,PlaceInformation,TravelHacks,Festivals, FamousPhotoPoint, Activities, Hotel,HotelCategory


class TaggitListFilter(SimpleListFilter):
    """Filter by taggit tags in admin."""
    title = _('tags')
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        tags = TaggedItem.tags_for(model_admin.model)
        return [(tag.name, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__name__in=[self.value()])


# =========================================================
# Admin for ALL pin-like models (13 models)
# =========================================================

class UnfoldLeafletMixin(ModelAdmin, LeafletGeoAdmin):
    """
    Shared admin for all pin-based models
    """

    # Hide system-managed fields
    exclude = ("slug", "created_by")

    # Show creator but prevent editing
    readonly_fields = ("created_by",)

    search_fields = ("name",)

    list_display = (
        "name",
        "city",
        "created_by",
        "published",
    )

    list_filter = ("published", "city", TaggitListFilter)

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

    def save_model(self, request, obj, form, change):
        """
        Logic:
        - If user submitted → created_by already set
        - If admin creates → created_by = admin
        - Admin CAN publish
        - User CANNOT publish
        """

        # Set creator only on first save
        if not change and not obj.created_by:
            obj.created_by = request.user

        # Non-staff users can never publish
        if not request.user.is_staff:
            obj.published = False

        super().save_model(request, obj, form, change)


# =========================================================
# Admin for HotelCategory (DIFFERENT MODEL)
# =========================================================

@admin.register(HotelCategory)
class HotelCategoryAdmin(ModelAdmin):
    search_fields = ("name",)

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

