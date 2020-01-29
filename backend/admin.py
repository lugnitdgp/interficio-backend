from django.contrib import admin
from backend.models import Player, Location, Level, Clue , FinalQuestion

from django.conf import settings


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'long',)
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'lat', 'long',)
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


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email', 'score', 'rank', 'current_level']
    # readonly_fields = ['map_qs']
    actions = ['clear_all_values', 'add_100_coins']

    def clear_all_values(self, req, queryset):
        queryset.update(score=0)
        queryset.update(rank=0)
        queryset.update(current_level=0)
        # queryset.update(map_qs=False)
    
    def add_100_coins(self, req, queryset):
        queryset.update(coins= 100)

    clear_all_values.short_description = "Clear all values"
    add_100_coins.short_description = "Add 100 coins"


class LevelAdmin(admin.ModelAdmin):
    list_display = ['title', 'paused', 'location']
    # readonly_fields = ['map_bool']

class ClueAdmin(admin.ModelAdmin):
    list_display = ['title', 'level']


admin.site.register(Location, LocationAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Clue, ClueAdmin)
admin.site.register(FinalQuestion)
