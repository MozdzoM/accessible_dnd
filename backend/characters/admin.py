from django.contrib import admin

from .models import Character, CharacterSkill, CharacterSpell


# Register your models here.
@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "level", "character_class", "race", "created_at")
    list_filter = ("character_class", "race", "background", "alignment")
    search_fields = ("name", "user__username")

admin.site.register(CharacterSkill)
admin.site.register(CharacterSpell)