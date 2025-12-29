from django.contrib.gis.db import models
 
 
class Country(models.Model):
    """Model for countries with geographical boundaries."""
    name = models.CharField(max_length=255, unique=True)
    geometry = models.GeometryField(srid=4326)
 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "countries"
        ordering = ["name"]
 
    def __str__(self):
        return self.name
 
 
class State(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="states"
    )
    name = models.CharField(max_length=255)
    geometry = models.MultiPolygonField(srid=4326)
 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "states"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["country", "name"],
                name="unique_state_per_country"
            )
        ]
 
    def __str__(self):
        return f"{self.name} ({self.country.name})"
 
 
class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=255)
    geometry = models.GeometryField(srid=4326)
 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "cities"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["state", "name"], name="unique_city_per_state")
        ]
 
    def __str__(self):
        return f"{self.name}, {self.state.name}"
 
 
 
 
class Specialzone(models.Model):
    """Model for special zones."""
    name = models.CharField(max_length=255, unique=True)
    geometry = models.GeometryField(srid=4326)
 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "special_zones"
        ordering = ["name"]
 
    def __str__(self):
        return self.name    