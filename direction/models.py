from django.db import models
from pins.models import MainAttraction, ThingsToDo,PlacesToVisit,PlacesToEat,Market,CountryInfo,DestinationGuide,PlaceInformation,TravelHacks,Festivals,FamousPhotoPoint,Activities,Hotel
 
class CTACategory(models.Model):
    """Model for call-to-action button categories."""
    name = models.CharField(max_length=100, unique=True)
    icon=models.CharField(max_length=50,blank=True,null=True)
    class Meta:
        db_table = "cta_categories"
        ordering = ["name"]
 
    def __str__(self):
        return self.name
    
class CTAButton(models.Model):
    """Model for call-to-action buttons linked to various pin types."""
    text = models.CharField(max_length=100)
 
    btncolor = models.CharField(
        max_length=50,
        blank=True,
        help_text="Button color (hex, name, or theme key)"
    )
 
    url = models.URLField()
 
    
    mainattraction= models.ForeignKey(
         MainAttraction,
         on_delete=models.CASCADE,blank=True,null=True
         
    )
    thingstodo= models.ForeignKey(
         ThingsToDo,
         on_delete=models.CASCADE,blank=True,null=True
 
    )   
    placestovisit= models.ForeignKey(
         PlacesToVisit,
         on_delete=models.CASCADE,blank=True,null=True
 
    )   
    placestoeat= models.ForeignKey(
         PlacesToEat,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    market= models.ForeignKey(
         Market,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    countryinfo= models.ForeignKey(
         CountryInfo,
         on_delete=models.CASCADE,blank=True,null=True  
 
    )
    destinationguide= models.ForeignKey(
         DestinationGuide,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    placeinformation= models.ForeignKey(
         PlaceInformation,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    travelhacks= models.ForeignKey(
         TravelHacks,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    festival= models.ForeignKey(
         Festivals,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    famousphotopoint= models.ForeignKey(
         FamousPhotoPoint,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    activites= models.ForeignKey(
         Activities,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    hotel= models.ForeignKey(
         Hotel,
         on_delete=models.CASCADE,blank=True,null=True
 
    )
    category = models.ForeignKey(
        "CTACategory",
        on_delete=models.CASCADE,
    )
 
    btn_ranking = models.IntegerField(
        default=0,
        help_text="Order of button within same pin"
    )
 
    cat_ranking = models.IntegerField(
        default=0,
        help_text="Order of category grouping"
    )
 
    btn_size = models.CharField(
        max_length=5,
        choices=[
            ("S", "Small"),
            ("M", "Medium"),
            ("L", "Large"),
            ("XL", "Extra Large"),
        ],
        default="M"
    )
 
    published = models.BooleanField(default=True)
 
    class Meta:
        db_table = "cta_buttons"
        ordering = ["cat_ranking", "btn_ranking"]
 
    def __str__(self):
        return f"{self.text}"