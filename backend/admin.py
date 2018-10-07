from django.contrib import admin
from backend.models import Player, Location , Level

from django.conf import settings

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'long',)
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ( 'name', 'lat', 'long',)
        }),
    )

    class Media:
        if hasattr(settings, 'GOOGLE_MAPS_API_KEY') and settings.GOOGLE_MAPS_API_KEY:
            css = {
                'all': ('css/admin/location_picker.css',),
            }
            js = (
                'https://maps.googleapis.com/maps/api/js?key={}'.format(settings.GOOGLE_MAPS_API_KEY),
                'js/admin/location_picker.js',
            )

# Register your models here.
admin.site.register(Location, LocationAdmin)
admin.site.register(Player)
admin.site.register(Level)