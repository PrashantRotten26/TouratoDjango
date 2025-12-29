from django.db import models
from location.models import Country, State, City, Specialzone
from pins.models import MainAttraction ,ThingsToDo,PlacesToVisit,PlacesToEat,Market,CountryInfo,DestinationGuide,PlaceInformation,TravelHacks,Festivals, FamousPhotoPoint, Activities, Hotel
# Create your models here.

class FAQ(models.Model):
    """Model for frequently asked questions related to locations and attractions."""
    question = models.CharField(max_length=100)
    answer = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True) 
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    specialZone = models.ForeignKey(Specialzone, on_delete=models.CASCADE, blank=True, null=True)
    mainattraction = models.ForeignKey(MainAttraction, on_delete=models.CASCADE, blank=True, null=True)    
    thingsToDo = models.ForeignKey(ThingsToDo, on_delete=models.CASCADE, blank=True, null=True)
    placestovisit=models.ForeignKey(PlacesToVisit,on_delete=models.CASCADE, blank=True, null=True)
    placesToEat=models.ForeignKey(PlacesToEat, on_delete=models.CASCADE, blank=True, null=True)
    market=models.ForeignKey(Market, on_delete=models.CASCADE, blank=True, null=True)
    countryinfo=models.ForeignKey(CountryInfo, on_delete=models.CASCADE, blank=True, null=True)
    DestinationGuide=models.ForeignKey(DestinationGuide, on_delete=models.CASCADE, blank=True, null=True)
    placeinformation=models.ForeignKey(PlaceInformation, on_delete=models.CASCADE, blank=True, null=True)
    travelhacks=models.ForeignKey(TravelHacks, on_delete=models.CASCADE, blank=True, null=True)
    Festivals=models.ForeignKey(Festivals, on_delete=models.CASCADE, blank=True, null=True)
    famousphotopoint=models.ForeignKey(FamousPhotoPoint, on_delete=models.CASCADE, blank=True, null=True)
    activites=models.ForeignKey(Activities, on_delete=models.CASCADE, blank=True, null=True)
    hotel=models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null=True)
