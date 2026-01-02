from django.db import models
from taggit.managers import TaggableManager
from location.models import Country,State,City,Specialzone  
from pins.models import MainAttraction,ThingsToDo,PlacesToVisit,PlacesToEat,Market,CountryInfo,DestinationGuide,PlaceInformation,TravelHacks,Festivals, FamousPhotoPoint, Activities, Hotel

class PostPlatform(models.Model):
    """
    Social media / content platforms (YouTube, Instagram, Website, Blog, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # short code like YT, IG 
    website = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_platforms"
        ordering = ["name"]
    
    def __str__(self):
        return self.name



class SocialPost(models.Model):
    """Model for social media posts linked to locations and attractions."""

    name = models.CharField(max_length=255)

    platform = models.ForeignKey(
    PostPlatform,
    on_delete=models.PROTECT,
    related_name="posts",
    null=True,          
    blank=True
)

    link = models.URLField(unique=True)

    description = models.TextField(blank=True)

    tags = TaggableManager(blank=True)

    language = models.CharField(max_length=50, blank=True,null=True)

    published = models.BooleanField(default=False)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    specialzone = models.ForeignKey(Specialzone, on_delete=models.CASCADE, blank=True, null=True)
    mainattraction = models.ForeignKey(MainAttraction, on_delete=models.CASCADE, blank=True, null=True)
    thingsToDo = models.ForeignKey(ThingsToDo, on_delete=models.CASCADE, blank=True, null=True)
    placestovisit = models.ForeignKey(PlacesToVisit, on_delete=models.CASCADE, blank=True, null=True)
    placesToEat = models.ForeignKey(PlacesToEat, on_delete=models.CASCADE, blank=True, null=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, blank=True, null=True)
    countryinfo = models.ForeignKey(CountryInfo, on_delete=models.CASCADE, blank=True, null=True)
    DestinationGuide = models.ForeignKey(DestinationGuide, on_delete=models.CASCADE, blank=True, null=True)
    placeinformation = models.ForeignKey(PlaceInformation, on_delete=models.CASCADE, blank=True, null=True)
    travelhacks = models.ForeignKey(TravelHacks, on_delete=models.CASCADE, blank=True, null=True)
    Festivals = models.ForeignKey(Festivals, on_delete=models.CASCADE, blank=True, null=True)
    famousphotopoint = models.ForeignKey(FamousPhotoPoint, on_delete=models.CASCADE, blank=True, null=True)
    activites = models.ForeignKey(Activities, on_delete=models.CASCADE, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
