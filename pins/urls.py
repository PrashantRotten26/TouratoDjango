from django.urls import path
from .views import all_pins, get_pins_by_type

urlpatterns = [
    path('api/all/', all_pins, name='all_pins'),
    path('api/pins/<str:table_name>/', get_pins_by_type, name='pins_by_type'),
]