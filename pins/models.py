import uuid
from django.db import models
from django.utils.text import slugify
from django.db.models import F
from django.contrib.gis.db import models as gis_models
from taggit.managers import TaggableManager
from location.models import City
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User



 
class MainAttraction(models.Model):
    """Model for main tourist attractions in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True,   
        help_text="URL-friendly identifier"
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
 
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "main_attractions"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_attraction_slug_per_city"
            )
        ]



    def save(self, *args, **kwargs):
        # Generate slug ONLY on object creation
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"mainattraction-{base_slug}-{random_suffix}"

        super().save(*args, **kwargs)

 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
class ThingsToDo(models.Model):
    """Model for activities or things to do in a city."""
    
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "things_to_do"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_things_to_do_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"thingstodo-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
    
 
 
class PlacesToVisit(models.Model):
    """Model for places to visit in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "places_to_visit"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_places_to_visit_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"placestovisit-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
 
 
class PlacesToEat(models.Model):
    """Model for places to eat in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "places_to_eat"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_places_to_eat_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"placestoeat-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
class Market(models.Model):
    """Model for markets and shopping areas in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "markets"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_market_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"market-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
class CountryInfo(models.Model):
    """Model for country-related information within a city context."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "country_info"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_country_info_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"countryinfo-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
class DestinationGuide(models.Model):
    """Model for destination guides within a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    pin = gis_models.PointField(
        srid=4326
    )
 
    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "destination_guides"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_destination_guide_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"destinationguide-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
class PlaceInformation(models.Model):
    """Model for detailed place-related information in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    pin = gis_models.PointField(
        srid=4326
    )
 
    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
 
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
 
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "place_information"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_place_information_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"placeinformation-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
 
 
class TravelHacks(models.Model):
    """Model for travel hacks and tips related to a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "travel_hacks"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_travel_hacks_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"travelhacks-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
 
class Festivals(models.Model):
    """Model for festivals and cultural events in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "festivals"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_festival_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"festivals-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
 
class FamousPhotoPoint(models.Model):
    """Model for famous photo points / photography spots in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "famous_photo_points"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_famous_photo_point_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"famousphotopoint-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
 
class Activities(models.Model):
    """Model for activities that can be done in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
 
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    published = models.BooleanField(default=False)
 
    link = models.URLField(blank=True, null=True)
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
 
    class Meta:
        db_table = "activities"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_activity_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"activities-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"
 
 
class HotelCategory(models.Model):
    """Model for hotel categories and classifications."""
 
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
 
    class Meta:
        db_table = "hotel_categories"
        ordering = ["name"]
 
    def __str__(self):
        return self.name
    
 
class Hotel(models.Model):
    """Model for hotels and accommodations in a city."""
 
    name = models.CharField(max_length=255)
 
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE
    )
 
    pin = gis_models.PointField(
        srid=4326
    )
    created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    slug = models.SlugField(
        max_length=255,
        blank=True   # ✅ REQUIRED (admin + auto slug)
    )
 
    description = models.TextField(blank=True)
    header_image = models.URLField(blank=True, null=True)
    icon = models.CharField(
        max_length=100,
        blank=True
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True
    )
    tags = TaggableManager(blank=True)
 
    category = models.ForeignKey(
        HotelCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
 
    rating = models.DecimalField(
    max_digits=4,
    decimal_places=2,
    null=True,
    blank=True,
    validators=[
        MinValueValidator(0),
        MaxValueValidator(5)
    ],
    help_text="Rating out of 5"
    )
    link = models.URLField(blank=True, null=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        db_table = "hotels"
        ordering = [F("rating").desc(nulls_last=True), "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"],
                name="unique_hotel_slug_per_city"
            )
        ]
 
    def save(self, *args, **kwargs):
        if not self.pk:
            base_slug = slugify(self.name)[:200]
            random_suffix = uuid.uuid4().hex[:5]
            self.slug = f"hotel-{base_slug}-{random_suffix}"
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.name} ({self.city.name})"


