from django.contrib import admin
from unfold.admin import ModelAdmin
from direction.models import CTAButton, CTACategory


@admin.register(CTACategory)
class CTACategoryAdmin(ModelAdmin):
    pass


@admin.register(CTAButton)
class CTAButtonAdmin(ModelAdmin):
    pass
