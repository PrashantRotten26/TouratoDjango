from django.contrib import admin
from unfold.admin import ModelAdmin

from faq.models import FAQ
@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    pass
