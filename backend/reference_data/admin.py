from django.contrib import admin

from .models import Alignment, Armor, Background, CharacterClass, Race, Skill, Spell, Weapon

# Register your models here.
for model in (CharacterClass, Race, Background, Alignment, Armor, Weapon, Skill, Spell):
    admin.site.register(model)